"""
测试不同的 Zotero 搜索方法
"""

from pyzotero import zotero

# 配置
library_id = "19092277"
api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"

zot = zotero.Zotero(library_id, 'user', api_key)

arxiv_id = "2512.24922v1"

print("=" * 70)
print("测试 Zotero API 搜索方法")
print("=" * 70)

# 方法1: 使用 q 参数 (通用搜索)
print("\n[方法1] q 参数通用搜索:")
results = zot.items(q=arxiv_id)
print(f"结果数: {len(results)}")

# 方法2: 指定字段格式的搜索 (Zotero API 高级搜索)
print("\n[方法2] 尝试字段限定搜索:")
# Zotero 支持特殊搜索语法
# 尝试不同的格式
test_queries = [
    f"archiveLocation:{arxiv_id}",
    f'archiveLocation:"{arxiv_id}"',
    f"{arxiv_id}",
]

for query in test_queries:
    print(f"\n  尝试查询: '{query}'")
    try:
        results = zot.items(q=query)
        print(f"  结果数: {len(results)}")
        if results:
            item = results[0]
            data = item.get('data', item)
            print(f"  第一个结果: {data.get('title', 'N/A')}")
    except Exception as e:
        print(f"  错误: {e}")

# 方法3: 使用添加时间排序获取最新
print("\n[方法3] 按日期排序获取最新项目:")
try:
    # Zotero API 支持排序参数
    recent = zot.items(sort='dateAdded', direction='desc', limit=20)
    print(f"最近20个项目:")

    for item in recent[:5]:
        data = item.get('data', item)
        print(f"  - key={data.get('key')[:8]}, archiveLocation={data.get('archiveLocation', '(空)')}, dateAdded={data.get('dateAdded', 'N/A')}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 70)
