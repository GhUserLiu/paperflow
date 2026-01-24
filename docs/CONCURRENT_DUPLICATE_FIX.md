# 并发去重修复说明

## 问题描述

在并发场景下，同一批次采集时可能出现**论文重复**的问题。

### 问题场景

1. **同一批次中有重复论文**：API 返回了相同的论文（例如 arXiv 和 ChinaXiv 返回同一篇论文的不同版本）
2. **并发执行**：两篇相同论文同时通过去重检查
3. **缓存未更新**：第一篇论文创建后，缓存未立即更新
4. **第二篇也创建成功**：导致重复

### 根本原因

```python
# 原有逻辑（有缺陷）：
def check_duplicate(self, identifier, identifier_field):
    # 1. 检查缓存（可能有延迟）
    if identifier in self._arxiv_id_cache:
        return cached_item_key

    # 2. 缓存未命中，查询 Zotero
    results = self.zot.items(...)

    # 3. ❌ 问题：创建新论文后，缓存不会更新！
    return None
```

**竞态条件（Race Condition）**：
- 论文 A 和论文 B 同时执行去重检查
- 两篇都通过了（缓存都为空）
- 论文 A 创建成功
- 论文 B 也创建成功 → **重复！**

## 解决方案

### 1. 新增本次运行跟踪集合

在 `ZoteroClient` 中添加 `_created_papers` 集合：

```python
# paperflow/clients/zotero_client.py:66-69
# 本次运行已创建的论文集合 (防止并发重复)
# Format: {field_value: identifier_field}
# Example: {"2301.12345": "archiveLocation", "chinaxiv123": "extra"}
self._created_papers: Dict[str, str] = {}
```

### 2. 优化去重检查顺序

```python
# paperflow/clients/zotero_client.py:347-357
def check_duplicate(self, identifier, identifier_field, collection_only):
    # ✅ 优先级1: 检查本次运行已创建的论文（内存操作，最快）
    identifier_clean = str(identifier).strip()
    if identifier_clean in self._created_papers:
        logger.info(f"从本次运行找到重复 (已在本次运行中创建)")
        return "RUNTIME_DUPLICATE"

    # 优先级2: 检查缓存（避免 API 调用）
    # ...

    # 优先级3: 查询 Zotero API
    # ...
```

### 3. 创建论文时记录到集合

```python
# paperflow/clients/zotero_client.py:225-249
def create_item(self, template_type, metadata):
    response = self.zot.create_items([template])

    if response["successful"]:
        item_key = ...

        # ✅ 记录到本次运行集合（防止并发重复）
        arxiv_id = metadata.get("archiveLocation", "").strip()
        if arxiv_id:
            self._created_papers[arxiv_id] = "archiveLocation"

        doi = metadata.get("DOI", "").strip()
        if doi:
            self._created_papers[doi] = "DOI"

        chinaxiv_id = extract_chinaxiv_id(metadata.get("extra", ""))
        if chinaxiv_id:
            self._created_papers[chinaxiv_id] = "extra"

        return item_key
```

### 4. 处理本次运行重复

```python
# paperflow/core/paper_processor.py:100-112
if existing_item_key:
    dup_type = "collection-only" if self.collection_only_dupcheck else "global"
    if existing_item_key == "RUNTIME_DUPLICATE":
        dup_type = "current run"  # 本次运行中的重复

    logger.info(f"Paper {paper_id} already exists ({dup_type}), skipping")
    return True  # 跳过重复论文
```

## 测试验证

运行测试验证修复：

```bash
python -m pytest tests/unit/test_concurrent_duplicate_detection.py -v
```

**测试覆盖**：
- ✅ 并发场景下的去重（`test_concurrent_duplicate_detection`）
- ✅ 已创建论文的跟踪（`test_created_papers_tracking`）
- ✅ 去重检查的优先级顺序（`test_check_duplicate_order`）

## 效果对比

### 修复前
```
[INFO] Processing paper: 2301.12345 (arxiv)
[INFO] Successfully created item with key: ABC123
[INFO] Processing paper: 2301.12345 (arxiv)  # ← 重复！
[INFO] Successfully created item with key: DEF456  # ← 重复创建！
```

### 修复后
```
[INFO] Processing paper: 2301.12345 (arxiv)
[INFO] Successfully created item with key: ABC123
[DEBUG] 记录 arXiv ID 到本次运行集合: 2301.12345

[INFO] Processing paper: 2301.12345 (arxiv)
[INFO] 从本次运行找到重复 archiveLocation '2301.12345' (已在本次运行中创建)
[INFO] Paper 2301.12345 (arxiv) already exists in library (current run, item: RUNTIME_DUPLICATE), skipping
```

## 技术细节

### 为什么使用内存集合？

1. **性能最优**：内存查找比 API 调用快 1000 倍以上
2. **即时更新**：创建后立即记录，无延迟
3. **线程安全**：在 `async with semaphore` 保护下执行
4. **自动清理**：程序结束时自动释放，无需手动维护

### 与缓存的区别

| 特性 | `_created_papers` (本次运行) | `_arxiv_id_cache` (持久缓存) |
|------|------------------------------|------------------------------|
| **作用域** | 本次运行 | 跨运行（5分钟TTL） |
| **更新时机** | 创建后立即更新 | 定期刷新（每5分钟） |
| **数据来源** | 本地创建 | Zotero API 查询 |
| **优先级** | **最高**（先查） | 次之 |
| **用途** | 防止并发重复 | 减少 API 调用 |

### 为什么不直接更新缓存？

1. **缓存是全局快照**：`_arxiv_id_cache` 存储的是 Zotero 库的快照（500篇论文）
2. **更新成本高**：需要重新查询 API 才能更新
3. **事务一致性**：缓存应该由专门的刷新逻辑维护，而不是在创建时修改

## 相关文件

- [paperflow/clients/zotero_client.py](../paperflow/clients/zotero_client.py) - 核心修复
- [paperflow/core/paper_processor.py](../paperflow/core/paper_processor.py) - 处理逻辑
- [tests/unit/test_concurrent_duplicate_detection.py](../tests/unit/test_concurrent_duplicate_detection.py) - 测试验证

## 版本历史

- **v2.1.1** (2026-01-24): 新增并发去重功能
- **v2.1.0** (2026-01-23): 初始版本（存在并发问题）
