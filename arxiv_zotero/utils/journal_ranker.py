"""
Journal Ranker - 基于多指标加权的论文排序器
期刊指标排序器 - 基于多指标加权综合评分
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class JournalRanker:
    """
    期刊指标排序器 - 基于多指标加权综合评分

    指标权重配置：
    - cited_by_percentile: 50% (被引百分位 - 最重要的指标)
    - h_index: 30% (h 指数 - 期刊影响力)
    - impact_factor: 20% (影响因子 - 传统指标)
    """

    # 默认权重配置
    DEFAULT_WEIGHTS = {
        'cited_by_percentile': 0.50,
        'h_index': 0.30,
        'impact_factor': 0.20
    }

    # 默认降级分数（无指标时的基准分）
    DEFAULT_SCORES = {
        'cited_by_percentile': 50.0,  # 默认中等水平
        'h_index': 10.0,  # 默认中等期刊
        'impact_factor': 1.0  # 默认低影响因子
    }

    # 指标归一化范围
    NORMALIZATION_RANGES = {
        'cited_by_percentile': (0, 100),  # 已经是百分位数
        'h_index': (1, 500),  # 常见期刊 h_index 范围
        'impact_factor': (0.1, 50)  # 常见影响因子范围
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        default_scores: Optional[Dict[str, float]] = None
    ):
        """
        初始化排序器

        Args:
            weights: 自定义权重配置
            default_scores: 自定义默认分数
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.default_scores = default_scores or self.DEFAULT_SCORES.copy()

        # 验证权重总和
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            for key in self.weights:
                self.weights[key] /= total_weight

        logger.info(f"JournalRanker initialized with weights: {self.weights}")

    def _normalize_value(self, value: float, metric_name: str) -> float:
        """
        将指标值归一化到 [0, 1] 范围

        Args:
            value: 原始值
            metric_name: 指标名称

        Returns:
            归一化后的值 (0-1)
        """
        min_val, max_val = self.NORMALIZATION_RANGES[metric_name]

        # 使用 min-max 归一化
        normalized = (value - min_val) / (max_val - min_val)

        # 限制在 [0, 1] 范围内
        return max(0.0, min(1.0, normalized))

    def _calculate_metric_score(
        self,
        metrics: Dict,
        metric_name: str
    ) -> float:
        """
        计算单个指标的得分

        Args:
            metrics: 论文指标数据
            metric_name: 指标名称

        Returns:
            该指标的得分 (0-100)
        """
        value = metrics.get(metric_name)

        if value is None or value == 0:
            # 使用默认分数
            value = self.default_scores[metric_name]
            logger.debug(f"Using default score for {metric_name}: {value}")

        # 归一化
        normalized = self._normalize_value(value, metric_name)

        # 转换为百分制
        return normalized * 100

    def calculate_composite_score(self, metrics: Dict) -> float:
        """
        计算综合评分

        公式：
        score = w1 * percentile_score + w2 * h_index_score + w3 * impact_factor_score

        Args:
            metrics: 包含指标的字典

        Returns:
            综合评分 (0-100)
        """
        scores = {}

        # 计算各指标得分
        for metric_name in ['cited_by_percentile', 'h_index', 'impact_factor']:
            scores[metric_name] = self._calculate_metric_score(metrics, metric_name)

        # 加权求和
        composite_score = sum(
            scores[name] * self.weights[name]
            for name in scores
        )

        logger.debug(f"Metric scores: {scores} -> Composite: {composite_score:.2f}")

        return composite_score

    def rank_papers(
        self,
        papers: List[Dict],
        metrics_map: Dict[str, Dict]
    ) -> List[Dict]:
        """
        对论文列表排序

        Args:
            papers: 论文列表
            metrics_map: paper_id -> metrics 映射

        Returns:
            排序后的论文列表（添加 openalex_score 字段）
        """
        # 为每篇论文计算综合评分
        for paper in papers:
            paper_id = (
                paper.get('arxiv_id') or
                paper.get('chinaxiv_id') or
                hash(paper.get('title', ''))
            )

            metrics = metrics_map.get(paper_id, {})
            score = self.calculate_composite_score(metrics)

            # 添加评分到论文数据
            paper['openalex_score'] = round(score, 2)
            paper['openalex_metrics'] = metrics

        # 按评分降序排序
        sorted_papers = sorted(
            papers,
            key=lambda p: p.get('openalex_score', 0),
            reverse=True
        )

        logger.info(f"Ranked {len(sorted_papers)} papers by OpenAlex score")

        return sorted_papers

    def get_ranking_summary(self, papers: List[Dict]) -> Dict:
        """
        获取排序统计摘要

        Args:
            papers: 已排序的论文列表

        Returns:
            统计信息字典
        """
        scores = [p.get('openalex_score', 0) for p in papers]

        return {
            'total_papers': len(papers),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'papers_with_metrics': sum(
                1 for p in papers
                if p.get('openalex_metrics', {}).get('source') != 'default'
            )
        }
