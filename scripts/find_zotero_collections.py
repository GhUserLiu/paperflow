#!/usr/bin/env python3
"""Find Zotero collection keys"""

from arxiv_zotero.clients.zotero_client import ZoteroClient
from arxiv_zotero.utils.credentials import load_credentials


def find_collections():
    """Find all collections in Zotero library"""
    print("[INFO] Loading credentials...")
    creds = load_credentials()

    client = ZoteroClient(library_id=creds["library_id"], api_key=creds["api_key"])

    print("\n[INFO] Fetching collections...")
    collections = client.zot.collections()

    if not collections:
        print("[INFO] No collections found in library")
        return

    print(f"\n[OK] Found {len(collections)} collection(s):\n")
    print(f"{'Collection Key':<25} {'Collection Name'}")
    print("-" * 60)

    for coll in collections:
        key = coll.get("key", "N/A")
        name = coll.get("data", {}).get("name", "Unnamed")
        print(f"{key:<25} {name}")

    print("\n[TIP] Copy the Collection Key and set it in your .env file:")
    print("      TEMP_COLLECTION_KEY=your_collection_key_here")


if __name__ == "__main__":
    find_collections()
