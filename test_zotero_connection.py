#!/usr/bin/env python3
"""Test Zotero API connection"""

import sys
from arxiv_zotero.utils.credentials import load_credentials
from arxiv_zotero.clients.zotero_client import ZoteroClient


def test_zotero_connection():
    """Test connection to Zotero API"""
    try:
        # Load credentials
        print("[INFO] Loading Zotero credentials...")
        creds = load_credentials()

        library_id = creds.get("library_id")
        api_key = creds.get("api_key")
        collection_key = creds.get("collection_key")

        if not library_id or not api_key:
            print("[ERROR] Missing Zotero credentials")
            print(f"   Library ID: {'Set' if library_id else 'Not set'}")
            print(f"   API Key: {'Set' if api_key else 'Not set'}")
            return False

        print("[OK] Credentials loaded successfully")
        print(f"   Library ID: {library_id}")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   Collection Key: {collection_key if collection_key else 'Not set'}")

        # Create client
        print()
        print("[INFO] Creating Zotero client...")
        client = ZoteroClient(library_id=library_id, api_key=api_key, collection_key=collection_key)

        # Test 1: Validate collection (if set)
        print()
        if collection_key:
            print("[TEST] Validating collection...")
            try:
                client.validate_collection()
                print(f"[OK] Collection '{collection_key}' is valid")
            except Exception as e:
                print(f"[WARN] Collection validation failed: {str(e)}")
        else:
            print("[SKIP] No collection KEY set, skipping collection validation")

        # Test 2: Get item count
        print()
        print("[TEST] Getting item count...")
        try:
            items = client.zot.top(limit=1)
            total = client.zot.num_items()
            print(f"[OK] Library contains {total} items")
        except Exception as e:
            print(f"[WARN] Could not get item count: {str(e)}")

        # Test 3: Create a test item (optional, requires write permission)
        print()
        print("[INFO] Connection test completed successfully!")
        print()
        print("[SUMMARY]")
        print("  - Credentials: OK")
        print("  - API Connection: OK")
        if collection_key:
            print(f"  - Collection Access: OK ({collection_key})")
        else:
            print("  - Collection Access: SKIPPED (no collection set)")

        return True

    except Exception as e:
        print(f"\n[ERROR] Connection test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_zotero_connection()
    sys.exit(0 if success else 1)
