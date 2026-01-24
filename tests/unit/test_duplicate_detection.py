"""
Duplicate Detection Test

This script tests the duplicate detection functionality of the arxiv-zotero-connector.
It runs the collection process twice and verifies that:
1. First run: Papers are added to Zotero
2. Second run: Duplicate papers are skipped (not added again)

Usage:
    python -m pytest tests/test_duplicate_detection.py -v
    or
    python tests/test_duplicate_detection.py
"""

import asyncio
import logging
from typing import Dict

import pytest

from paperflow import ArxivSearchParams, ArxivZoteroCollector

# Configure logging to see the duplicate detection messages
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_duplicate_detection():
    """
    Test duplicate detection by running collection twice.

    Expected behavior:
    - First run: Add 5 papers to general collection
    - Second run: Skip all 5 papers (duplicates)
    """

    # Configuration
    zotero_library_id = "19092277"
    zotero_api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"
    collection_key = "LRML5CDJ"  # general collection

    # Search parameters - small batch for testing
    search_params = ArxivSearchParams(
        keywords=['"autonomous driving" AND perception'],
        max_results=5,
        categories=["cs.CV", "cs.RO"],
    )

    # Create collector
    collector = ArxivZoteroCollector(
        zotero_library_id=zotero_library_id,
        zotero_api_key=zotero_api_key,
        collection_key=collection_key,
    )

    print("=" * 70)
    print("DUPLICATE DETECTION TEST")
    print("=" * 70)
    print()

    # First run - should add papers
    print("[FIRST RUN] - Adding papers to Zotero...")
    print("-" * 70)

    successful_1, failed_1 = await collector.run_manual_collection_async(
        search_params=search_params, download_pdfs=False  # Skip PDFs for faster testing
    )

    print()
    print(f"First Run Results:")
    print(f"  Successful: {successful_1} papers")
    print(f"  Failed: {failed_1} papers")
    print()

    # Second run - should skip duplicates
    print("[SECOND RUN] - Checking for duplicates...")
    print("-" * 70)

    successful_2, failed_2 = await collector.run_manual_collection_async(
        search_params=search_params, download_pdfs=False
    )

    print()
    print(f"Second Run Results:")
    print(f"  Successful: {successful_2} papers (should all be skipped duplicates)")
    print(f"  Failed: {failed_2} papers")
    print()

    # Verify results
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    if successful_2 == successful_1 and failed_2 == 0:
        print("✓ PASS: Duplicate detection is working correctly!")
        print(f"  All {successful_2} papers were identified as duplicates and skipped.")
        return True
    else:
        print("✗ FAIL: Duplicate detection may not be working properly.")
        print(f"  Expected: {successful_1} successful, 0 failed")
        print(f"  Got: {successful_2} successful, {failed_2} failed")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_duplicate_detection())
    exit(0 if result else 1)
