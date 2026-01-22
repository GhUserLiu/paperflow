import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..clients.arxiv_client import ArxivClient
from ..clients.chinaxiv_client import ChinaXivClient
from ..clients.openalex_client import OpenAlexClient
from ..clients.zotero_client import ZoteroClient
from ..config.arxiv_config import ARXIV_TO_ZOTERO_MAPPING
from ..config.bilingual_config import BilingualConfig
from ..config.metadata_config import MetadataMapper
from ..utils.credentials import load_credentials
from ..utils.journal_ranker import JournalRanker
from ..utils.pdf_manager import PDFManager
from ..utils.summarizer import PaperSummarizer
from .paper_processor import PaperProcessor
from .search_params import ArxivSearchParams

# Setup logs directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR /
            "arxiv_zotero.log",
            mode="a",
            encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class ArxivZoteroCollector:
    def __init__(
        self,
        zotero_library_id: str,
        zotero_api_key: str,
        collection_key: str = None,
        summarizer: Optional[PaperSummarizer] = None,
        config: Optional[dict] = None,
        enable_chinaxiv: bool = False,
        enable_openalex_ranking: bool = False,
        openalex_weights: Optional[Dict] = None,
        collection_only_dupcheck: bool = False,
    ):
        """
        Initialize the ArxivZoteroCollector

        Args:
            zotero_library_id: Zotero library ID
            zotero_api_key: Zotero API key
            collection_key: Zotero collection key (optional)
            summarizer: PaperSummarizer instance (optional)
            config: Configuration dictionary (optional)
            enable_chinaxiv: Enable ChinaXiv source (default: False)
            enable_openalex_ranking: Enable OpenAlex journal ranking (default: False)
            openalex_weights: Custom weights for OpenAlex metrics (optional)
            collection_only_dupcheck: Enable collection-only duplicate checking (default: False)
        """
        self.collection_key = collection_key
        self.zotero_client = ZoteroClient(
            zotero_library_id, zotero_api_key, collection_key)
        self.metadata_mapper = MetadataMapper(ARXIV_TO_ZOTERO_MAPPING)
        self.pdf_manager = PDFManager()
        self.paper_processor = PaperProcessor(
            self.zotero_client, self.metadata_mapper, self.pdf_manager, summarizer, config
        )
        self.arxiv_client = ArxivClient()
        self.chinaxiv_client = ChinaXivClient() if enable_chinaxiv else None
        self.enable_chinaxiv = enable_chinaxiv
        self.async_session = None

        # Initialize OpenAlex ranking
        self.enable_openalex_ranking = enable_openalex_ranking
        self.openalex_client = None
        self.journal_ranker = None

        if enable_openalex_ranking:
            self.openalex_client = OpenAlexClient()
            self.journal_ranker = JournalRanker(weights=openalex_weights)
            logger.info("OpenAlex ranking enabled")

        # Set collection-only duplicate checking
        if collection_only_dupcheck:
            self.paper_processor.set_collection_only_dupcheck(True)

    def search_arxiv(self, search_params: ArxivSearchParams) -> List[Dict]:
        """Search arXiv using provided search parameters"""
        return self.arxiv_client.search_arxiv(search_params)

    def search_chinaxiv(self, search_params: ArxivSearchParams) -> List[Dict]:
        """Search ChinaXiv using provided search parameters"""
        if not self.enable_chinaxiv:
            logger.warning(
                "ChinaXiv is not enabled. Use enable_chinaxiv=True when initializing the collector."
            )
            return []
        return self.chinaxiv_client.search_chinaxiv(search_params)

    def search_all_sources(
            self, search_params: ArxivSearchParams) -> List[Dict]:
        """
        Search all enabled sources (arXiv and ChinaXiv)
        搜索所有启用的来源（arXiv 和 ChinaXiv）
        """
        all_papers = []

        # Search arXiv
        logger.info("Searching arXiv...")
        arxiv_papers = self.search_arxiv(search_params)
        logger.info(f"Found {len(arxiv_papers)} papers from arXiv")
        all_papers.extend(arxiv_papers)

        # Search ChinaXiv if enabled
        if self.enable_chinaxiv:
            logger.info("Searching ChinaXiv...")
            chinaxiv_papers = self.search_chinaxiv(search_params)
            logger.info(f"Found {len(chinaxiv_papers)} papers from ChinaXiv")
            all_papers.extend(chinaxiv_papers)
        else:
            logger.info("ChinaXiv is disabled, skipping...")

        logger.info(f"Total papers from all sources: {len(all_papers)}")

        # Apply OpenAlex ranking if enabled
        if self.enable_openalex_ranking:
            all_papers = self.rank_papers_with_openalex(all_papers)

        return all_papers

    def rank_papers_with_openalex(self, papers: List[Dict]) -> List[Dict]:
        """
        使用 OpenAlex 指标对论文排序
        Rank papers using OpenAlex journal metrics

        Args:
            papers: List of paper metadata dictionaries

        Returns:
            Sorted list of papers with openalex_score field added
        """
        if not self.enable_openalex_ranking or not papers:
            return papers

        try:
            logger.info(
                f"Ranking {len(papers)} papers with OpenAlex metrics...")

            # Batch preload metrics
            metrics_map = self.openalex_client.preload_journal_metrics(papers)

            # Rank papers
            ranked_papers = self.journal_ranker.rank_papers(
                papers, metrics_map)

            # Output statistics
            summary = self.journal_ranker.get_ranking_summary(ranked_papers)
            logger.info(
                f"OpenAlex ranking complete: "
                f"Avg={summary['avg_score']:.1f}, "
                f"Max={summary['max_score']:.1f}, "
                f"Min={summary['min_score']:.1f}, "
                f"Papers with metrics={summary['papers_with_metrics']}/{summary['total_papers']}"
            )

            return ranked_papers

        except Exception as e:
            logger.error(f"Error in OpenAlex ranking: {str(e)}")
            return papers

    async def run_collection_async(
        self,
        search_params: ArxivSearchParams,
        download_pdfs: bool = True,
        use_all_sources: bool = False,
    ) -> Tuple[int, int]:
        """
        Run collection process asynchronously using search parameters

        Args:
            search_params: Search parameters
            download_pdfs: Whether to download PDFs
            use_all_sources: If True, search all enabled sources; if False, only search arXiv
        """
        try:
            if use_all_sources:
                papers = self.search_all_sources(search_params)
            else:
                papers = self.search_arxiv(search_params)
            logger.info(f"Found {len(papers)} papers matching the criteria")

            if not papers:
                return 0, 0

            successful = 0
            failed = 0

            async def process_paper(paper):
                nonlocal successful, failed
                try:
                    if await self.paper_processor.process_paper(paper, download_pdfs):
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Error processing paper: {str(e)}")

            tasks = [process_paper(paper) for paper in papers]
            await asyncio.gather(*tasks)

            logger.info(
                f"Collection complete. Successfully processed {successful} papers. Failed: {failed}"
            )

            # 输出 API 统计信息
            api_stats = self.zotero_client.get_api_stats()
            logger.info(
                f"API 请求统计: {api_stats['total_requests']} 次, "
                f"耗时 {api_stats['elapsed_time']:.1f} 秒, "
                f"平均速率 {api_stats['rate']:.2f} 次/秒, "
                f"缓存条目 {api_stats['cache_size']} 条"
            )

            return successful, failed

        except Exception as e:
            logger.error(f"Error in run_collection: {str(e)}")
            return 0, 0

    async def run_bilingual_collection_async(
        self,
        category: str,
        start_date,
        config_path: Optional[str] = None,
        download_pdfs: bool = True,
    ) -> Tuple[int, int]:
        """
        Run bilingual collection using config file with different keywords for each source
        使用配置文件运行双语采集，为不同来源使用不同的关键词

        Args:
            category: Research category (e.g., 'general', 'communication')
            start_date: Filter papers published after this date
            config_path: Path to bilingual config YAML file
            download_pdfs: Whether to download PDFs

        Returns:
            Tuple of (successful_count, failed_count)
        """
        try:
            # Load bilingual configuration
            # 加载双语配置
            bilingual_config = BilingualConfig(config_path)

            all_papers = []

            # Search arXiv with English keywords
            # 使用英文关键词搜索 arXiv
            if bilingual_config.is_source_enabled("arxiv"):
                logger.info(
                    f"Searching arXiv for category '{category}' with English keywords...")
                arxiv_keywords = bilingual_config.get_keywords_for_source(
                    "arxiv", category)
                arxiv_max_results = bilingual_config.get_max_results_for_source(
                    "arxiv")

                for keyword in arxiv_keywords:
                    search_params = ArxivSearchParams(
                        keywords=[keyword],
                        start_date=start_date,
                        max_results=arxiv_max_results
                        # Divide results among keywords
                        // len(arxiv_keywords),
                    )
                    arxiv_papers = self.search_arxiv(search_params)
                    all_papers.extend(arxiv_papers)
                    logger.info(
                        f"  arXiv keyword '{keyword}': {len(arxiv_papers)} papers")

                # Limit total arXiv results
                all_papers = all_papers[:arxiv_max_results]
                logger.info(
                    f"Total from arXiv (limited to {arxiv_max_results}): {len(all_papers)}")

            # Search ChinaXiv with Chinese keywords
            # 使用中文关键词搜索 ChinaXiv
            chinaxiv_papers_count = 0
            if bilingual_config.is_source_enabled(
                    "chinaxiv") and self.enable_chinaxiv:
                logger.info(
                    f"Searching ChinaXiv for category '{category}' with Chinese keywords..."
                )
                chinaxiv_keywords = bilingual_config.get_keywords_for_source(
                    "chinaxiv", category)
                chinaxiv_max_results = bilingual_config.get_max_results_for_source(
                    "chinaxiv")

                chinaxiv_results = []
                for keyword in chinaxiv_keywords:
                    search_params = ArxivSearchParams(
                        keywords=[keyword],
                        start_date=start_date,
                        max_results=chinaxiv_max_results // len(
                            chinaxiv_keywords),
                    )
                    papers = self.search_chinaxiv(search_params)
                    chinaxiv_results.extend(papers)
                    logger.info(
                        f"  ChinaXiv keyword '{keyword}': {len(papers)} papers")

                # Limit total ChinaXiv results
                chinaxiv_results = chinaxiv_results[:chinaxiv_max_results]
                all_papers.extend(chinaxiv_results)
                chinaxiv_papers_count = len(chinaxiv_results)
                logger.info(
                    f"Total from ChinaXiv (limited to {chinaxiv_max_results}): {chinaxiv_papers_count}"
                )

            logger.info(f"Total papers from all sources: {len(all_papers)}")

            if not all_papers:
                return 0, 0

            # Process all papers
            successful = 0
            failed = 0

            async def process_paper(paper):
                nonlocal successful, failed
                try:
                    if await self.paper_processor.process_paper(paper, download_pdfs):
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Error processing paper: {str(e)}")

            tasks = [process_paper(paper) for paper in all_papers]
            await asyncio.gather(*tasks)

            logger.info(
                f"Bilingual collection complete. Successful: {successful}, Failed: {failed}"
            )

            # Output API statistics
            api_stats = self.zotero_client.get_api_stats()
            logger.info(
                f"API 请求统计: {api_stats['total_requests']} 次, "
                f"耗时 {api_stats['elapsed_time']:.1f} 秒, "
                f"平均速率 {api_stats['rate']:.2f} 次/秒, "
                f"缓存条目 {api_stats['cache_size']} 条"
            )

            return successful, failed

        except Exception as e:
            logger.error(f"Error in run_bilingual_collection: {str(e)}")
            return 0, 0

    async def close(self):
        """Cleanup resources"""
        if self.async_session:
            await self.async_session.close()
        self.zotero_client.close()
        await self.pdf_manager.close()

        # Cleanup OpenAlex client
        if self.openalex_client:
            self.openalex_client.close()


async def main():
    collector = None
    try:
        credentials = load_credentials()
        collector = ArxivZoteroCollector(
            zotero_library_id=credentials["library_id"],
            zotero_api_key=credentials["api_key"],
            collection_key=credentials["collection_key"],
        )

        # Example usage with ArxivSearchParams
        search_params = ArxivSearchParams(
            keywords=["multi-agent systems"], max_results=10, categories=["cs.AI"]
        )

        successful, failed = await collector.run_collection_async(
            search_params=search_params, download_pdfs=True
        )

        logger.info(
            f"Script completed. Successfully processed: {successful}, Failed: {failed}")

    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
    finally:
        if collector:
            await collector.close()


if __name__ == "__main__":
    asyncio.run(main())
