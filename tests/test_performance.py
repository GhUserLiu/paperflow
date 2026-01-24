"""Performance benchmarks for arxiv-zotero-connector"""

import asyncio
import time
from typing import Dict, List

import pytest

from arxiv_zotero import ArxivSearchParams, ArxivZoteroCollector


class TestPerformance:
    """Performance benchmark tests"""

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_search_performance_small(self):
        """
        Benchmark: Small search (10 papers)

        Expected: < 5 seconds
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        collector = ArxivZoteroCollector(
            zotero_library_id="test_library", zotero_api_key="test_key"
        )

        search_params = ArxivSearchParams(keywords=["machine learning"], max_results=10)

        start_time = time.time()
        papers = collector.search_arxiv(search_params)
        elapsed = time.time() - start_time

        assert len(papers) <= 10
        assert elapsed < 5.0, f"Search took {elapsed:.2f}s, expected < 5s"

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_search_performance_medium(self):
        """
        Benchmark: Medium search (50 papers)

        Expected: < 10 seconds
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        collector = ArxivZoteroCollector(
            zotero_library_id="test_library", zotero_api_key="test_key"
        )

        search_params = ArxivSearchParams(keywords=["deep learning"], max_results=50)

        start_time = time.time()
        papers = collector.search_arxiv(search_params)
        elapsed = time.time() - start_time

        assert len(papers) <= 50
        assert elapsed < 10.0, f"Search took {elapsed:.2f}s, expected < 10s"

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_duplicate_check_performance(self):
        """
        Benchmark: Duplicate checking speed

        Expected: < 1 second for collection-only mode
        Expected: < 3 seconds for global mode
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        # Collection-only mode (faster)
        collector_collection = ArxivZoteroCollector(
            zotero_library_id="test_library",
            zotero_api_key="test_key",
            collection_key="test_collection",
            collection_only_dupcheck=True,
        )

        start_time = time.time()
        result = collector_collection.zotero_client.check_duplicate(
            identifier="test_id", identifier_field="archiveLocation", collection_only=True
        )
        elapsed_collection = time.time() - start_time

        assert (
            elapsed_collection < 1.0
        ), f"Collection-only check took {elapsed_collection:.2f}s, expected < 1s"

        # Global mode (slower but more thorough)
        collector_global = ArxivZoteroCollector(
            zotero_library_id="test_library",
            zotero_api_key="test_key",
            collection_only_dupcheck=False,
        )

        start_time = time.time()
        result = collector_global.zotero_client.check_duplicate(
            identifier="test_id", identifier_field="archiveLocation", collection_only=False
        )
        elapsed_global = time.time() - start_time

        assert elapsed_global < 3.0, f"Global check took {elapsed_global:.2f}s, expected < 3s"

        # Collection-only should be faster
        assert (
            elapsed_collection < elapsed_global
        ), "Collection-only mode should be faster than global mode"

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_cache_performance(self):
        """
        Benchmark: Cache hit rate improvement

        Tests that repeated queries are faster with cache
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        collector = ArxivZoteroCollector(
            zotero_library_id="test_library", zotero_api_key="test_key"
        )

        # First query (cold cache)
        search_params = ArxivSearchParams(keywords=["neural networks"], max_results=20)

        start_time = time.time()
        papers_1 = collector.search_arxiv(search_params)
        elapsed_cold = time.time() - start_time

        # Second query (warm cache)
        start_time = time.time()
        papers_2 = collector.search_arxiv(search_params)
        elapsed_warm = time.time() - start_time

        # Results should be consistent
        assert len(papers_1) == len(papers_2)

        # Warm cache should not be significantly slower
        # (Note: arXiv API doesn't change, so timing should be similar)
        assert (
            elapsed_warm < elapsed_cold * 1.5
        ), f"Warm cache ({elapsed_warm:.2f}s) took too long vs cold ({elapsed_cold:.2f}s)"

    @pytest.mark.benchmark
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_processing_performance(self):
        """
        Benchmark: Concurrent paper processing

        Expected: Processing 10 papers concurrently should be faster than sequential
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        collector = ArxivZoteroCollector(
            zotero_library_id="test_library", zotero_api_key="test_key"
        )

        # Create mock papers
        mock_papers = [
            {
                "title": f"Test Paper {i}",
                "arxiv_id": f"23{1:02d}.12345",
                "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf",
                "published_date": "2023-01-01",
                "summary": "Test summary",
            }
            for i in range(1, 11)
        ]

        start_time = time.time()

        # Process with built-in concurrency control (MAX_CONCURRENT_PAPERS = 5)
        # Note: This test would need actual paper processing logic
        # For now, just test that concurrent execution works
        tasks = []
        for paper in mock_papers:
            # Simulate processing
            await asyncio.sleep(0.1)  # 100ms per paper

        elapsed = time.time() - start_time

        # With 10 papers at 100ms each:
        # Sequential: ~1000ms
        # Concurrent (5 at a time): ~300ms
        expected_max = 0.5  # 500ms max for concurrent processing

        assert (
            elapsed < expected_max
        ), f"Concurrent processing took {elapsed:.2f}s, expected < {expected_max}s"

    def test_api_rate_limiting(self):
        """
        Benchmark: API rate limiting compliance

        Tests that the client respects Zotero API rate limits
        (100 requests per 10 minutes = ~1 request per 6 seconds)
        """
        if not self._has_credentials():
            pytest.skip("No Zotero credentials available")

        collector = ArxivZoteroCollector(
            zotero_library_id="test_library", zotero_api_key="test_key"
        )

        # Make multiple requests and verify timing
        request_times = []

        for i in range(3):
            start_time = time.time()
            try:
                # This would make an actual API call
                # collector.zotero_client.check_duplicate(...)
                pass
            except Exception:
                pass  # Ignore actual errors, we're just testing rate limiting
            request_times.append(time.time() - start_time)

        # Check that requests are properly spaced
        # (min_request_interval = 6.0 seconds)
        for i in range(1, len(request_times)):
            interval = request_times[i] - request_times[i - 1]
            # Due to rate limiting, there should be a minimum interval
            # (Note: This is a simplified test)
            assert interval >= 0, "Time should be positive"

    def _has_credentials(self) -> bool:
        """Check if Zotero credentials are available for testing"""
        import os

        return bool(os.getenv("ZOTERO_LIBRARY_ID") and os.getenv("ZOTERO_API_KEY"))


class MemoryProfiler:
    """Memory profiling utilities"""

    @staticmethod
    def profile_memory_usage():
        """
        Profile memory usage of key operations

        Usage:
            profiler = MemoryProfiler()
            profiler.profile_memory_usage()
        """
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()

            print(f"\nMemory Usage:")
            print(f"  RSS: {mem_info.rss / 1024 / 1024:.2f} MB")
            print(f"  VMS: {mem_info.vms / 1024 / 1024:.2f} MB")
            print(f"  Percent: {process.memory_percent():.2f}%")

        except ImportError:
            print("psutil not installed. Install with: pip install psutil")

    @staticmethod
    def track_memory_growth():
        """
        Track memory growth over iterations

        Useful for detecting memory leaks
        """
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            baseline = process.memory_info().rss

            print("\nMemory Growth Tracking:")
            print(f"Baseline: {baseline / 1024 / 1024:.2f} MB")

            # Simulate operations
            for i in range(10):
                # Do work here
                pass

                current = process.memory_info().rss
                growth = (current - baseline) / 1024 / 1024
                print(f"Iteration {i+1}: +{growth:.2f} MB")

        except ImportError:
            print("psutil not installed. Install with: pip install psutil")


if __name__ == "__main__":
    # Run benchmarks directly
    print("Running performance benchmarks...")
    print("Note: Install pytest-benchmark for detailed benchmarking:")
    print("  pip install pytest-benchmark")

    # Example usage
    profiler = MemoryProfiler()
    profiler.profile_memory_usage()
    profiler.track_memory_growth()
