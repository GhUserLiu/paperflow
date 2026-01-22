"""
OpenAlex API Client
OpenAlex API 客户端 - 用于查询期刊指标数据
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class OpenAlexClient:
    """
    OpenAlex API 客户端，用于查询期刊指标数据

    支持的查询方式：
    1. DOI 查询（优先）
    2. 期刊名称查询（降级）
    3. 本地缓存查询（最快）

    API 文档: https://docs.openalex.org/
    """

    # OpenAlex API 基础 URL
    BASE_URL = "https://api.openalex.org"

    # API 速率限制配置
    RATE_LIMIT_DELAY = 0.3  # 秒（优化：实测安全值，免费版限制：每秒 1 次请求）
    MAX_RETRIES = 3
    TIMEOUT = 30

    # 默认指标值（降级使用）
    DEFAULT_PERCENTILE = 50.0  # 默认中等被引百分位
    DEFAULT_H_INDEX = 10.0  # 默认中等期刊 h 指数
    DEFAULT_IMPACT_FACTOR = 1.0  # 默认低影响因子

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化 OpenAlex 客户端

        Args:
            cache_dir: 缓存目录路径，默认为 config/journal_metrics_cache.json
        """
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "config"
        self.cache_file = self.cache_dir / "journal_metrics_cache.json"
        self.metrics_cache = {}

        # 初始化 HTTP session
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "arxiv-zotero-connector", "Accept": "application/json"}
        )

        # 加载本地缓存
        self._load_cache()

        logger.info(f"OpenAlexClient initialized with cache: {self.cache_file}")

    def _load_cache(self):
        """从本地文件加载期刊指标缓存"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 兼容新旧格式
                    if isinstance(data, dict) and "metrics" in data:
                        self.metrics_cache = data["metrics"]
                    else:
                        self.metrics_cache = data
                logger.info(f"Loaded {len(self.metrics_cache)} cached journal metrics")
            else:
                self.metrics_cache = {}
                logger.info("No existing cache found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            self.metrics_cache = {}

    def _save_cache(self):
        """保存期刊指标缓存到本地文件"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # 使用新格式（包含元数据）
            data = {
                "metadata": {
                    "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "total_entries": len(self.metrics_cache),
                    "version": "1.0",
                },
                "metrics": self.metrics_cache,
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.metrics_cache)} journal metrics to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    def query_by_doi(self, doi: str) -> Optional[Dict]:
        """
        通过 DOI 查询论文的期刊指标

        Args:
            doi: 论文 DOI（例如：10.1038/nature12373）

        Returns:
            Dict containing:
                - cited_by_percentile: float (0-100)
                - h_index: int
                - impact_factor: float
                - journal_name: str
                - source: str (来源标识)
        """
        if not doi:
            return None

        # 标准化 DOI（移除前缀）
        clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()

        # 检查缓存
        cache_key = f"doi:{clean_doi}"
        if cache_key in self.metrics_cache:
            logger.debug(f"Cache hit for DOI: {clean_doi}")
            return self.metrics_cache[cache_key]

        # 查询 OpenAlex API
        try:
            url = f"{self.BASE_URL}/works/https://doi.org/{clean_doi}"
            response = self._make_request(url)

            if response and response.status_code == 200:
                data = response.json()
                metrics = self._extract_metrics_from_work(data)

                if metrics:
                    # 保存到缓存
                    self.metrics_cache[cache_key] = metrics
                    self._save_cache()
                    logger.info(f"Retrieved metrics for DOI: {clean_doi}")
                    return metrics

        except Exception as e:
            logger.error(f"Error querying DOI {clean_doi}: {str(e)}")

        return None

    def query_by_journal_name(self, journal_name: str) -> Optional[Dict]:
        """
        通过期刊名称查询期刊指标

        Args:
            journal_name: 期刊名称（例如：Nature, Science）

        Returns:
            Dict containing:
                - h_index: int
                - impact_factor: float
                - journal_name: str
                - source: str (来源标识)
        """
        if not journal_name:
            return None

        # 清理期刊名称
        clean_name = self._clean_journal_name(journal_name)

        # 检查缓存
        cache_key = f"journal:{clean_name}"
        if cache_key in self.metrics_cache:
            logger.debug(f"Cache hit for journal: {clean_name}")
            return self.metrics_cache[cache_key]

        # 查询 OpenAlex API
        try:
            # 使用 OpenAlex 的 sources API
            filter_query = f"display_name.search:{clean_name}"
            url = f"{self.BASE_URL}/sources?filter={filter_query}"

            response = self._make_request(url)

            if response and response.status_code == 200:
                data = response.json()

                if data.get("results") and len(data["results"]) > 0:
                    # 获取最匹配的期刊（第一个结果）
                    source = data["results"][0]
                    metrics = self._extract_metrics_from_source(source)

                    if metrics:
                        # 保存到缓存
                        self.metrics_cache[cache_key] = metrics
                        self._save_cache()
                        logger.info(f"Retrieved metrics for journal: {clean_name}")
                        return metrics

        except Exception as e:
            logger.error(f"Error querying journal {clean_name}: {str(e)}")

        return None

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        发送 HTTP 请求（带重试和速率限制）

        Args:
            url: 请求 URL

        Returns:
            Response object or None if failed
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                # 速率限制
                time.sleep(self.RATE_LIMIT_DELAY)

                response = self.session.get(url, timeout=self.TIMEOUT)

                if response.status_code == 429:  # Rate limited
                    wait_time = 2**attempt  # 指数退避
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                return response

            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RATE_LIMIT_DELAY * (attempt + 1))

        return None

    def _extract_metrics_from_work(self, work_data: Dict) -> Optional[Dict]:
        """
        从 OpenAlex work 数据提取指标

        Args:
            work_data: OpenAlex API 返回的 work 数据

        Returns:
            Dict of metrics or None
        """
        try:
            # 获取期刊来源信息
            source = work_data.get("primary_source")
            if not source:
                return None

            # 提取指标
            metrics = {
                "cited_by_percentile": work_data.get("cited_by_percentile", {}).get("value"),
                "h_index": source.get("h_index"),
                "impact_factor": source.get("impact_factor"),
                "journal_name": source.get("display_name"),
                "source": "openalex_work_api",
            }

            # 过滤 None 值
            return {k: v for k, v in metrics.items() if v is not None}

        except Exception as e:
            logger.error(f"Error extracting metrics from work: {str(e)}")
            return None

    def _extract_metrics_from_source(self, source_data: Dict) -> Optional[Dict]:
        """
        从 OpenAlex source 数据提取指标

        Args:
            source_data: OpenAlex API 返回的 source 数据

        Returns:
            Dict of metrics or None
        """
        try:
            metrics = {
                "h_index": source_data.get("h_index"),
                "impact_factor": source_data.get("impact_factor"),
                "journal_name": source_data.get("display_name"),
                "source": "openalex_source_api",
            }

            # 过滤 None 值
            return {k: v for k, v in metrics.items() if v is not None}

        except Exception as e:
            logger.error(f"Error extracting metrics from source: {str(e)}")
            return None

    def _clean_journal_name(self, journal_ref: str) -> str:
        """
        从 journal_ref 提取期刊名称并清理

        Args:
            journal_ref: 原始期刊引用字符串

        Returns:
            清理后的期刊名称
        """
        if not journal_ref:
            return ""

        # 提取期刊名称（去除卷号、页码等）
        # 例如："Nature 500 (2013) 123-145" -> "Nature"
        # 例如："IEEE Trans. Neural Networks" -> "IEEE Trans. Neural Networks"

        # 尝试提取第一个单词序列（期刊名通常在开头）
        match = re.match(r"^([A-Za-z\s\.\&]+)", journal_ref)
        if match:
            name = match.group(1).strip()
            # 清理多余的空格和点号
            name = re.sub(r"\s+", " ", name)
            return name

        return journal_ref

    def get_metrics_for_paper(self, paper: Dict) -> Dict:
        """
        为论文获取完整的指标数据（综合查询策略）

        查询策略：
        1. 优先使用 DOI 查询（最准确）
        2. 无 DOI 时从 journal_ref 提取期刊名查询
        3. 都没有则返回默认空指标

        Args:
            paper: 论文元数据字典

        Returns:
            Dict containing:
                - cited_by_percentile: float or None
                - h_index: int or None
                - impact_factor: float or None
                - journal_name: str or None
                - source: str (查询来源)
        """
        # 策略 1: 尝试 DOI 查询
        doi = paper.get("doi")
        if doi:
            logger.debug(f"Querying by DOI: {doi}")
            metrics = self.query_by_doi(doi)
            if metrics:
                return metrics

        # 策略 2: 尝试期刊名称查询
        journal_ref = paper.get("journal_ref")
        if journal_ref:
            journal_name = self._clean_journal_name(journal_ref)
            if journal_name:
                logger.debug(f"Querying by journal name: {journal_name}")
                metrics = self.query_by_journal_name(journal_name)
                if metrics:
                    return metrics

        # 策略 3: 返回默认空指标
        logger.debug(
            f"No metrics found for paper: {
                paper.get(
                    'title',
                    'Unknown')[
                    :50]}"
        )
        return self._get_default_metrics()

    def _get_default_metrics(self) -> Dict:
        """返回默认指标（确保系统不会崩溃）"""
        return {
            "cited_by_percentile": self.DEFAULT_PERCENTILE,
            "h_index": self.DEFAULT_H_INDEX,
            "impact_factor": self.DEFAULT_IMPACT_FACTOR,
            "journal_name": "Unknown",
            "source": "default",
        }

    def preload_journal_metrics(self, papers: List[Dict]) -> Dict[str, Dict]:
        """
        批量预加载期刊指标（优化版）

        Args:
            papers: 论文列表

        Returns:
            Dict mapping paper_id to metrics
        """
        results = {}
        start_time = time.time()

        for i, paper in enumerate(papers):
            paper_id = paper.get("arxiv_id") or paper.get("chinaxiv_id") or str(i)
            metrics = self.get_metrics_for_paper(paper)
            results[paper_id] = metrics

            # 进度日志
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                logger.info(
                    f"Preloaded metrics for {i + 1}/{len(papers)} papers ({rate:.1f} papers/sec)"
                )

        elapsed = time.time() - start_time
        logger.info(
            f"Preloaded metrics for {len(results)} papers in {elapsed:.1f}s ({len(results) / elapsed:.1f} papers/sec)"
        )
        return results

    def auto_preload_common_journals(self, silent: bool = False) -> bool:
        """
        自动预加载常见期刊指标（当缓存为空时）

        Args:
            silent: 是否静默模式（不打印提示）

        Returns:
            bool: 是否成功执行预热
        """
        # 检查缓存文件大小
        if self.cache_file.exists():
            size_mb = self.cache_file.stat().st_size / (1024 * 1024)
            if size_mb > 0.1:
                # 缓存已存在且有内容，跳过预热
                logger.info(
                    f"Cache already exists ({
                        size_mb:.2f} MB), skipping preload"
                )
                return False

        # 常见计算机科学期刊（精简版，只加载最常用的）
        common_journals = [
            # 综合类顶刊
            "Nature",
            "Science",
            "PNAS",
            # AI/ML 顶刊顶会
            "NeurIPS",
            "ICML",
            "ICLR",
            "AAAI",
            "IJCAI",
            # 计算机机视觉
            "CVPR",
            "ICCV",
            "ECCV",
            # NLP
            "ACL",
            "EMNLP",
            # 期刊
            "Journal of Machine Learning Research",
            "Machine Learning",
            "IEEE Transactions on Pattern Analysis and Machine Intelligence",
            "IEEE Transactions on Neural Networks and Learning Systems",
            "Artificial Intelligence",
            # 自动驾驶相关
            "IEEE Transactions on Intelligent Transportation Systems",
        ]

        if not silent:
            logger.info(
                f"Auto-preloading {len(common_journals)} common journals (first-time setup)..."
            )

        success_count = 0
        for journal in common_journals:
            try:
                result = self.query_by_journal_name(journal)
                if result:
                    success_count += 1
            except Exception as e:
                logger.debug(f"Failed to preload {journal}: {e}")

        logger.info(
            f"Auto-preload complete: {success_count}/{len(common_journals)} journals cached"
        )
        return True

    def close(self):
        """清理资源"""
        if self.session:
            self.session.close()
        # 确保存缓存
        self._save_cache()
