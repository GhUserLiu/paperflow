"""
JournalRanker 单元测试 | JournalRanker Unit Tests
"""

import pytest
from arxiv_zotero.utils.journal_ranker import JournalRanker


class TestJournalRanker:
    """JournalRanker 测试"""

    def test_init_default_weights(self):
        """测试使用默认权重初始化"""
        ranker = JournalRanker()

        assert ranker.weights == {
            'cited_by_percentile': 0.50,
            'h_index': 0.30,
            'impact_factor': 0.20
        }
        assert ranker.default_scores == {
            'cited_by_percentile': 50.0,
            'h_index': 10.0,
            'impact_factor': 1.0
        }

    def test_init_custom_weights(self):
        """测试使用自定义权重初始化"""
        custom_weights = {
            'cited_by_percentile': 0.70,
            'h_index': 0.20,
            'impact_factor': 0.10
        }
        ranker = JournalRanker(weights=custom_weights)

        assert ranker.weights == custom_weights

    def test_init_weights_normalization(self):
        """测试权重自动归一化"""
        # 权重总和不为 1
        invalid_weights = {
            'cited_by_percentile': 0.5,
            'h_index': 0.5,
            'impact_factor': 0.5  # 总和 = 1.5
        }
        ranker = JournalRanker(weights=invalid_weights)

        # 应该自动归一化
        assert abs(sum(ranker.weights.values()) - 1.0) < 0.01

    def test_init_custom_default_scores(self):
        """测试自定义默认分数"""
        custom_defaults = {
            'cited_by_percentile': 40.0,
            'h_index': 5.0,
            'impact_factor': 0.5
        }
        ranker = JournalRanker(default_scores=custom_defaults)

        assert ranker.default_scores == custom_defaults

    def test_normalize_value_percentile(self):
        """测试百分位归一化"""
        ranker = JournalRanker()

        # 百分位范围是 [0, 100]
        assert ranker._normalize_value(0, 'cited_by_percentile') == 0.0
        assert ranker._normalize_value(100, 'cited_by_percentile') == 1.0
        assert ranker._normalize_value(50, 'cited_by_percentile') == 0.5

        # 超出范围的值应该被截断
        assert ranker._normalize_value(-10, 'cited_by_percentile') == 0.0
        assert ranker._normalize_value(150, 'cited_by_percentile') == 1.0

    def test_normalize_value_h_index(self):
        """测试 h 指数归一化"""
        ranker = JournalRanker()

        # h_index 范围是 [1, 500]
        assert ranker._normalize_value(1, 'h_index') == 0.0
        assert ranker._normalize_value(500, 'h_index') == 1.0
        # (250-1)/(500-1) = 249/499 ≈ 0.499
        assert abs(ranker._normalize_value(250, 'h_index') - 0.499) < 0.001

    def test_normalize_value_impact_factor(self):
        """测试影响因子归一化"""
        ranker = JournalRanker()

        # impact_factor 范围是 [0.1, 50]
        assert ranker._normalize_value(0.1, 'impact_factor') == 0.0
        assert ranker._normalize_value(50, 'impact_factor') == 1.0
        # (25-0.1)/(50-0.1) = 24.9/49.9 ≈ 0.499
        assert abs(ranker._normalize_value(25, 'impact_factor') - 0.499) < 0.001

    def test_calculate_metric_score_with_value(self):
        """测试计算指标得分（有值）"""
        ranker = JournalRanker()

        metrics = {'cited_by_percentile': 95.5}
        score = ranker._calculate_metric_score(metrics, 'cited_by_percentile')

        # 95.5 在 [0, 100] 范围内归一化后应该是 0.955
        # 转换为百分制: 95.5
        assert abs(score - 95.5) < 0.1

    def test_calculate_metric_score_with_none(self):
        """测试计算指标得分（无值，使用默认）"""
        ranker = JournalRanker()

        metrics = {}  # 没有指标值
        score = ranker._calculate_metric_score(metrics, 'cited_by_percentile')

        # 应该使用默认值 50.0
        # 50.0 在 [0, 100] 范围内归一化后是 0.5
        # 转换为百分制: 50.0
        assert abs(score - 50.0) < 0.1

    def test_calculate_metric_score_with_zero(self):
        """测试计算指标得分（值为0，使用默认）"""
        ranker = JournalRanker()

        metrics = {'h_index': 0}
        score = ranker._calculate_metric_score(metrics, 'h_index')

        # 0 应该使用默认值 10.0
        # 10.0 在 [1, 500] 范围内归一化后是 (10-1)/(500-1) = 0.018
        # 转换为百分制: 1.8
        assert abs(score - 1.8) < 0.1

    def test_calculate_composite_score_all_metrics(self):
        """测试计算综合评分（完整指标）"""
        ranker = JournalRanker()

        # 高影响力论文
        metrics = {
            'cited_by_percentile': 95.5,
            'h_index': 250,
            'impact_factor': 14.255
        }

        score = ranker.calculate_composite_score(metrics)

        # 验证分数在合理范围内
        assert 0 <= score <= 100
        # 高影响力论文应该有较高的分数
        assert score > 50

    def test_calculate_composite_score_default_fallback(self):
        """测试计算综合评分（使用默认分数）"""
        ranker = JournalRanker()

        metrics = {}  # 没有任何指标

        score = ranker.calculate_composite_score(metrics)

        # 应该使用所有默认值
        # percentile: 50 -> 0.5 -> 50
        # h_index: 10 -> 0.018 -> 1.8
        # impact_factor: 1.0 -> 0.018 -> 1.8
        # 加权: 0.5*50 + 0.3*1.8 + 0.2*1.8 = 25 + 0.54 + 0.36 = 25.9
        assert 25 <= score <= 27

    def test_calculate_composite_score_partial_metrics(self):
        """测试计算综合评分（部分指标）"""
        ranker = JournalRanker()

        # 只有被引百分位
        metrics = {'cited_by_percentile': 90.0}

        score = ranker.calculate_composite_score(metrics)

        # percentile: 90 -> 0.9 -> 90
        # h_index: 默认 10 -> ~1.8
        # impact_factor: 默认 1.0 -> ~1.8
        # 加权: 0.5*90 + 0.3*1.8 + 0.2*1.8 = 45 + 0.54 + 0.36 = 45.9
        assert 45 <= score <= 47

    def test_rank_papers_basic(self):
        """测试基本论文排序"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Paper A', 'arxiv_id': '2401.00001'},
            {'title': 'Paper B', 'arxiv_id': '2401.00002'},
            {'title': 'Paper C', 'arxiv_id': '2401.00003'}
        ]

        metrics_map = {
            '2401.00001': {'cited_by_percentile': 90.0, 'h_index': 200, 'impact_factor': 10.0},
            '2401.00002': {'cited_by_percentile': 50.0, 'h_index': 50, 'impact_factor': 2.0},
            '2401.00003': {'cited_by_percentile': 95.0, 'h_index': 300, 'impact_factor': 15.0}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        # 验证排序结果
        assert len(ranked) == 3
        # Paper C 应该排在第一（最高指标）
        assert ranked[0]['arxiv_id'] == '2401.00003'
        # Paper A 应该排在第二
        assert ranked[1]['arxiv_id'] == '2401.00001'
        # Paper B 应该排在第三
        assert ranked[2]['arxiv_id'] == '2401.00002'

        # 验证所有论文都有 openalex_score 字段
        for paper in ranked:
            assert 'openalex_score' in paper
            assert 'openalex_metrics' in paper

    def test_rank_papers_with_chinaxiv_id(self):
        """测试包含 ChinaXiv ID 的论文排序"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Chinese Paper', 'chinaxiv_id': 'CN123456'}
        ]

        metrics_map = {
            'CN123456': {'cited_by_percentile': 80.0, 'h_index': 100, 'impact_factor': 5.0}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        assert len(ranked) == 1
        assert ranked[0]['chinaxiv_id'] == 'CN123456'
        assert 'openalex_score' in ranked[0]

    def test_rank_papers_no_id(self):
        """测试没有 ID 的论文（使用 title hash）"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Paper without ID'}
        ]

        # 使用 hash(title) 作为 key
        title_hash = hash('Paper without ID')
        metrics_map = {
            title_hash: {'cited_by_percentile': 70.0}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        assert len(ranked) == 1
        assert 'openalex_score' in ranked[0]

    def test_rank_papers_missing_metrics(self):
        """测试部分论文缺少指标数据"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Paper A', 'arxiv_id': '2401.00001'},
            {'title': 'Paper B', 'arxiv_id': '2401.00002'}  # 没有指标数据
        ]

        metrics_map = {
            '2401.00001': {'cited_by_percentile': 90.0, 'h_index': 200, 'impact_factor': 10.0}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        assert len(ranked) == 2
        # Paper A 有指标，应该有较高分数
        assert ranked[0]['arxiv_id'] == '2401.00001'
        assert ranked[0]['openalex_score'] > 20
        # Paper B 使用默认分数，分数较低
        assert ranked[1]['arxiv_id'] == '2401.00002'
        assert ranked[1]['openalex_score'] < 30

    def test_get_ranking_summary(self):
        """测试获取排序摘要"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Paper A', 'openalex_score': 80.5, 'openalex_metrics': {'source': 'openalex_work_api'}},
            {'title': 'Paper B', 'openalex_score': 60.0, 'openalex_metrics': {'source': 'openalex_work_api'}},
            {'title': 'Paper C', 'openalex_score': 40.0, 'openalex_metrics': {'source': 'default'}}
        ]

        summary = ranker.get_ranking_summary(papers)

        assert summary['total_papers'] == 3
        assert abs(summary['avg_score'] - 60.17) < 0.1  # (80.5 + 60 + 40) / 3
        assert summary['max_score'] == 80.5
        assert summary['min_score'] == 40.0
        assert summary['papers_with_metrics'] == 2  # 只有2篇论文有实际指标（非default）

    def test_get_ranking_summary_empty(self):
        """测试空列表的排序摘要"""
        ranker = JournalRanker()

        summary = ranker.get_ranking_summary([])

        assert summary['total_papers'] == 0
        assert summary['avg_score'] == 0
        assert summary['max_score'] == 0
        assert summary['min_score'] == 0
        assert summary['papers_with_metrics'] == 0

    def test_custom_weights_ranking(self):
        """测试自定义权重的排序结果"""
        # 强调被引百分位的权重
        custom_weights = {
            'cited_by_percentile': 0.80,
            'h_index': 0.15,
            'impact_factor': 0.05
        }
        ranker = JournalRanker(weights=custom_weights)

        papers = [
            {'title': 'Paper A', 'arxiv_id': '2401.00001'},
            {'title': 'Paper B', 'arxiv_id': '2401.00002'}
        ]

        # Paper A: 高 percentile (95), 低 h_index 和 impact_factor
        # Paper B: 中等 percentile (80), 但最高 h_index 和 impact_factor
        metrics_map = {
            '2401.00001': {'cited_by_percentile': 95.0, 'h_index': 10, 'impact_factor': 1.0},
            '2401.00002': {'cited_by_percentile': 80.0, 'h_index': 500, 'impact_factor': 50.0}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        # Paper B 排第一（虽然 percentile 较低，但完美的 h_index 和 impact_factor 补偿了）
        # 计算：Paper A: 0.8*95 + 0.15*1.8 + 0.05*1.8 ≈ 76.4
        #       Paper B: 0.8*80 + 0.15*100 + 0.05*100 = 84.0
        assert ranked[0]['arxiv_id'] == '2401.00002'
        assert ranked[0]['openalex_score'] > ranked[1]['openalex_score']

    def test_score_rounding(self):
        """测试分数四舍五入"""
        ranker = JournalRanker()

        papers = [
            {'title': 'Paper', 'arxiv_id': '2401.00001'}
        ]

        metrics_map = {
            '2401.00001': {'cited_by_percentile': 87.432, 'h_index': 123.456, 'impact_factor': 5.678}
        }

        ranked = ranker.rank_papers(papers, metrics_map)

        # 分数应该四舍五入到2位小数
        score = ranked[0]['openalex_score']
        assert len(str(score).split('.')[-1]) <= 2
