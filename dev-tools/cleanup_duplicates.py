"""
清理测试期间产生的重复论文
"""

from pyzotero import zotero

# 配置
library_id = "19092277"
api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"

zot = zotero.Zotero(library_id, 'user', api_key)

print("=" * 70)
print("清理测试产生的重复论文")
print("=" * 70)

# 获取最近的项目
recent = zot.items(sort='dateAdded', direction='desc', limit=20)

# 需要删除的重复论文 (保留最早添加的)
duplicates = {}  # arxiv_id -> [items]

for item in recent:
    data = item.get('data', item)
    arxiv_id = data.get('archiveLocation', '')

    if arxiv_id:
        if arxiv_id not in duplicates:
            duplicates[arxiv_id] = []
        duplicates[arxiv_id].append(data)

# 找出重复并删除多余的
deleted_count = 0
for arxiv_id, items in duplicates.items():
    if len(items) > 1:
        print(f"\n发现重复: {arxiv_id}")
        # 按添加时间排序,保留最早的,删除其余的
        items_sorted = sorted(items, key=lambda x: x.get('dateAdded', ''))

        to_keep = items_sorted[0]
        to_delete = items_sorted[1:]

        print(f"  保留: {to_keep['key']} (添加于 {to_keep.get('dateAdded', 'N/A')})")

        for item in to_delete:
            try:
                item_key = item.get('key') if isinstance(item, dict) else item
                zot.delete_item(item_key)
                date_added = item.get('dateAdded', 'N/A') if isinstance(item, dict) else 'N/A'
                print(f"  删除: {item_key} (添加于 {date_added})")
                deleted_count += 1
            except Exception as e:
                item_key = item.get('key') if isinstance(item, dict) else item
                print(f"  删除失败 {item_key}: {e}")

print(f"\n" + "=" * 70)
print(f"清理完成! 共删除 {deleted_count} 个重复条目")
print("=" * 70)
