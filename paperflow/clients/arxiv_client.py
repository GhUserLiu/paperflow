import asyncio
import logging
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import arxiv
import pytz

from ..core.search_params import ArxivSearchParams

logger = logging.getLogger(__name__)


class ArxivClient:
    """
    Enhanced arXiv client with intelligent search strategies

    Features:
    - Multi-keyword combination search
    - Category-based filtering and statistics
    - Smart retry and timeout handling
    - Search quality analysis
    """

    # Popular arXiv categories for reference
    POPULAR_CATEGORIES = {
        "cs.AI": "Artificial Intelligence",
        "cs.LG": "Machine Learning",
        "cs.CV": "Computer Vision",
        "cs.CL": "Computation and Language",
        "cs.CR": "Cryptography and Security",
        "stat.ML": "Machine Learning (Statistics)",
        "math.OC": "Optimization and Control",
        "eess.SP": "Signal Processing",
        "physics.app-ph": "Applied Physics",
        "physics.comp-ph": "Computational Physics",
    }

    def __init__(self, max_retries: int = 3, delay_seconds: float = 3.0):
        """
        Initialize the ArxivClient

        Args:
            max_retries: Maximum number of retries for failed requests
            delay_seconds: Delay between API requests to respect rate limits
        """
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=delay_seconds,
            num_retries=max_retries
        )
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    def filter_by_date(
        self, result: arxiv.Result, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> bool:
        """
        Filter arxiv result by date range

        Args:
            result: arXiv search result
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            True if result falls within date range
        """
        if not (start_date or end_date):
            return True

        pub_date = result.published.astimezone(pytz.UTC)

        # Ensure start_date and end_date are timezone-aware
        if start_date:
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=pytz.UTC)
            if pub_date < start_date:
                return False

        if end_date:
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=pytz.UTC)
            if pub_date > end_date:
                return False

        return True

    def suggest_search_strategy(self, keywords: List[str]) -> Dict[str, str]:
        """
        Suggest optimal search strategy based on keywords

        Args:
            keywords: List of search keywords

        Returns:
            Dictionary with search suggestions
        """
        suggestions = {
            "query_type": "basic",
            "recommended_query": "",
            "tips": []
        }

        if len(keywords) == 0:
            suggestions["tips"].append("Please provide at least one keyword")
            return suggestions

        if len(keywords) == 1:
            # Single keyword - simple search
            suggestions["query_type"] = "simple"
            suggestions["recommended_query"] = f'all:" "{keywords[0]}"'
            suggestions["tips"].append("Single keyword search - results may be broad")

        elif len(keywords) == 2:
            # Two keywords - AND search
            suggestions["query_type"] = "and"
            suggestions["recommended_query"] = f'all: "{keywords[0]}" AND all: "{keywords[1]}"'
            suggestions["tips"].append("AND search - papers must contain both keywords")
            suggestions["tips"].append("Use OR for broader search: all: "keyword1" OR all: "keyword2"")

        else:
            # Multiple keywords - complex search
            suggestions["query_type"] = "complex"
            query_parts = [f'all: "{kw}"' for kw in keywords[:3]]
            suggestions["recommended_query"] = " AND ".join(query_parts)
            suggestions["tips"].append(f"Using top 3 keywords for search: {', '.join(keywords[:3])}")
            suggestions["tips"].append("Consider splitting into multiple searches for better coverage")

        # Add category suggestions
        suggestions["tips"].append("Add category filter for targeted results, e.g., cat:cs.AI")
        suggestions["tips"].append("Use ti: for title-only search, e.g., ti:neural network")

        return suggestions

    def build_smart_query(
        self,
        keywords: List[str],
        categories: Optional[List[str]] = None,
        title_only: bool = False,
        abstract_only: bool = False
    ) -> str:
        """
        Build an optimized arXiv search query

        Args:
            keywords: List of keywords
            categories: Optional list of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
            title_only: Search in title only
            abstract_only: Search in abstract only

        Returns:
            Optimized query string
        """
        if not keywords:
            return "all:*"

        # Choose search field
        field = "ti" if title_only else ("abs" if abstract_only else "all")

        # Build keyword part
        if len(keywords) == 1:
            keyword_query = f'{field}: "{keywords[0]}"'
        else:
            # Use AND for multiple keywords
            keyword_parts = [f'{field}: "{kw}"' for kw in keywords]
            keyword_query = f"({keyword_parts[0]})"
            for kw_part in keyword_parts[1:]:
                keyword_query += f" AND {kw_part}"

        # Add category filter if specified
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            return f"({keyword_query}) AND ({cat_query})"

        return keyword_query

    def filter_by_content_type(self, result: arxiv.Result, content_type: Optional[str]) -> bool:
        """Filter arxiv result by content type"""
        if not content_type:
            return True

        comment = getattr(result, "comment", "") or ""
        journal_ref = getattr(result, "journal_ref", "") or ""

        comment = comment.lower()
        journal_ref = journal_ref.lower()

        if content_type == "journal":
            return bool(
                journal_ref and not ("preprint" in journal_ref or "submitted" in journal_ref)
            )
        elif content_type == "conference":
            return bool(
                "conference" in comment
                or "proceedings" in comment
                or "conference" in journal_ref
                or "proceedings" in journal_ref
            )
        elif content_type == "preprint":
            return not bool(journal_ref)

        return True

    async def _prepare_arxiv_metadata(self, result: arxiv.Result) -> Optional[Dict]:
        """
        Prepare metadata from arxiv result

        Args:
            result: arXiv search result

        Returns:
            Dictionary with paper metadata or None if error
        """
        try:
            return {
                "title": result.title,
                "abstract": result.summary,
                "authors": [author.name for author in result.authors],
                "published": (
                    result.published.strftime("%Y-%m-%d")
                    if isinstance(result.published, datetime)
                    else result.published
                ),
                "arxiv_id": result.entry_id.split("/")[-1],
                "arxiv_url": result.entry_id,
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category,
                "categories": result.categories,
                "journal_ref": getattr(result, "journal_ref", None),
                "doi": getattr(result, "doi", None),
                "comment": getattr(result, "comment", None),
                "source": "arxiv",
            }
        except Exception as e:
            logger.error(f"Error preparing arxiv metadata: {str(e)}")
            return None

    def search_arxiv(self, search_params: ArxivSearchParams) -> List[Dict]:
        """
        Search arXiv using provided search parameters

        Args:
            search_params: Search parameters including keywords, categories, dates

        Returns:
            List of paper metadata dictionaries
        """
        start_time = time.time()
        stats = {
            "total_fetched": 0,
            "filtered_date": 0,
            "filtered_content": 0,
            "errors": 0,
        }

        try:
            query = search_params.build_query()
            logger.info(f"🔍 Executing arXiv search")
            logger.info(f"   Query: {query}")
            logger.info(f"   Max results: {search_params.max_results}")

            # Show search suggestions
            suggestions = self.suggest_search_strategy(search_params.keywords or [])
            if suggestions["tips"]:
                logger.info(f"💡 Search tips: {suggestions['tips'][0]}")

            search = arxiv.Search(
                query=query,
                max_results=search_params.max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            papers = []

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []

                for result in self.client.results(search):
                    stats["total_fetched"] += 1

                    # Apply date filter
                    if not self.filter_by_date(
                        result, search_params.start_date, search_params.end_date
                    ):
                        stats["filtered_date"] += 1
                        continue

                    # Apply content type filter
                    if not self.filter_by_content_type(result, search_params.content_type):
                        stats["filtered_content"] += 1
                        continue

                    # Prepare metadata asynchronously
                    future = executor.submit(asyncio.run, self._prepare_arxiv_metadata(result))
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    try:
                        paper_metadata = future.result(timeout=30)
                        if paper_metadata:
                            papers.append(paper_metadata)
                    except Exception as e:
                        stats["errors"] += 1
                        logger.warning(f"Error processing paper: {str(e)}")

            elapsed = time.time() - start_time

            # Log search statistics
            logger.info(f"✅ Search completed in {elapsed:.2f}s")
            logger.info(f"   Results: {len(papers)} papers (fetched: {stats['total_fetched']}, "
                       f"filtered by date: {stats['filtered_date']}, "
                       f"filtered by content: {stats['filtered_content']}, "
                       f"errors: {stats['errors']})")

            # Analyze results if we have papers
            if papers:
                self._log_search_statistics(papers)

            return papers

        except arxiv.HTTPError as e:
            logger.error(f"❌ arXiv HTTP Error: {e.status} - {e.message}")
            logger.error("   This might be due to rate limiting. Try again later.")
            return []
        except Exception as e:
            logger.error(f"❌ Error searching arXiv: {str(e)}")
            return []

    def _log_search_statistics(self, papers: List[Dict]) -> None:
        """
        Log statistics about search results

        Args:
            papers: List of paper metadata
        """
        if not papers:
            return

        # Category distribution
        categories = []
        for paper in papers:
            if paper.get("primary_category"):
                categories.append(paper["primary_category"])

        if categories:
            cat_counter = Counter(categories)
            top_categories = cat_counter.most_common(5)
            logger.info(f"   Top categories: {', '.join([f'{cat} ({count})' for cat, count in top_categories])}")

        # Date range
        dates = [paper.get("published") for paper in papers if paper.get("published")]
        if dates:
            logger.info(f"   Date range: {min(dates)} to {max(dates)}")

        # Papers with DOI
        with_doi = sum(1 for paper in papers if paper.get("doi"))
        logger.info(f"   Papers with DOI: {with_doi}/{len(papers)} ({100*with_doi/len(papers):.1f}%)")

        # Papers published in journals
        with_journal = sum(1 for paper in papers if paper.get("journal_ref"))
        if with_journal > 0:
            logger.info(f"   Papers in journals: {with_journal}/{len(papers)} ({100*with_journal/len(papers):.1f}%)")
