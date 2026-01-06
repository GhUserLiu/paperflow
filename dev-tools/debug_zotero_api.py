"""
调试 Zotero API 返回的数据结构
"""

from pyzotero import zotero

# 配置
library_id = "19092277"
api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"

# 创建客户端
zot = zotero.Zotero(library_id, 'user', api_key)

# 测试查询 arXiv ID
arxiv_id = "2512.24922v1"

print("=" * 70)
print(f"搜索 arXiv ID: {arxiv_id}")
print("=" * 70)

# 方法1: 使用 q 参数查询
print("\n[方法1] 使用 q 参数:")
results = zot.items(q=arxiv_id)
print(f"返回结果数量: {len(results)}")

if results:
    print(f"\n第一个结果的结构:")
    first_item = results[0]
    print(f"  类型: {type(first_item)}")
    print(f"  键: {first_item.keys() if isinstance(first_item, dict) else 'N/A'}")

    if isinstance(first_item, dict):
        if 'data' in first_item:
            print(f"\n  data 字段内容:")
            data = first_item['data']
            print(f"    key: {data.get('key')}")
            print(f"    title: {data.get('title')}")
            print(f"    archiveLocation: {data.get('archiveLocation')}")
            print(f"    DOI: {data.get('DOI')}")
        else:
            print(f"\n  没有 data 字段")
            print(f"    key: {first_item.get('key')}")
            print(f"    title: {first_item.get('title')}")
            print(f"    archiveLocation: {first_item.get('archiveLocation')}")
            print(f"    DOI: {first_item.get('DOI')}")

# 方法2: 获取所有项目并手动过滤
print("\n" + "=" * 70)
print("[方法2] 获取所有项目并手动过滤:")
all_items = zot.items()
print(f"总项目数: {len(all_items)}")

# 查找匹配的
found = False
for item in all_items:
    item_data = item.get('data', item) if isinstance(item, dict) else item
    field_value = item_data.get('archiveLocation', '')

    if field_value and str(field_value).strip() == arxiv_id.strip():
        print(f"\n找到匹配!")
        print(f"  item key: {item_data.get('key')}")
        print(f"  title: {item_data.get('title')}")
        print(f"  archiveLocation: {field_value}")
        found = True
        break

if not found:
    print(f"\n未找到 archiveLocation='{arxiv_id}' 的项目")

    # 列出最近几个项目的 archiveLocation
    print(f"\n最近5个项目的 archiveLocation:")
    count = 0
    for item in all_items[:5]:
        item_data = item.get('data', item) if isinstance(item, dict) else item
        print(f"  key={item_data.get('key')}, archiveLocation={item_data.get('archiveLocation', '(空)')}")
        count += 1
