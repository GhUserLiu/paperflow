"""
Bilingual Keywords Configuration Loader
双语关键词配置加载器
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class BilingualConfig:
    """Bilingual keywords configuration manager"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize bilingual configuration

        Args:
            config_path: Path to YAML config file (default: config/bilingual_keywords.yaml)
        """
        if config_path is None:
            # Default to config/bilingual_keywords.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "bilingual_keywords.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()

            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            logger.info(f"Loaded bilingual config from {self.config_path}")
            return config

        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "global": {"time_filter_hours": 25, "download_pdfs": True, "total_max_results": 50},
            "sources": {
                "arxiv": {"enabled": True, "language": "en", "max_results": 25, "keywords": {}},
                "chinaxiv": {
                    "enabled": False,  # Disabled by default
                    "language": "zh",
                    "max_results": 25,
                    "keywords": {},
                },
            },
            "collections": {},
            "sorting": {"method": "date", "order": "descending"},
        }

    def is_source_enabled(self, source: str) -> bool:
        """Check if a source is enabled"""
        return self.config.get("sources", {}).get(source, {}).get("enabled", False)

    def get_keywords_for_source(self, source: str, category: str = None) -> List[str]:
        """
        Get keywords for a specific source and category

        Args:
            source: 'arxiv' or 'chinaxiv'
            category: Optional category name (e.g., 'general', 'communication')

        Returns:
            List of keyword strings
        """
        source_config = self.config.get("sources", {}).get(source, {})
        keywords_config = source_config.get("keywords", {})

        if category:
            # Get keywords for specific category
            keywords = keywords_config.get(category, [])
        else:
            # Get all keywords as a list
            if isinstance(keywords_config, dict):
                keywords = list(keywords_config.values())
            else:
                keywords = keywords_config if isinstance(keywords_config, list) else []

        return keywords

    def get_max_results_for_source(self, source: str) -> int:
        """Get max results for a specific source"""
        return self.config.get("sources", {}).get(source, {}).get("max_results", 25)

    def get_collection_key(self, category: str) -> Optional[str]:
        """Get Zotero collection key for a category"""
        return self.config.get("collections", {}).get(category)

    def get_time_filter_hours(self) -> int:
        """Get time filter in hours"""
        return self.config.get("global", {}).get("time_filter_hours", 25)

    def get_all_categories(self) -> List[str]:
        """Get list of all configured categories"""
        arxiv_keywords = self.config.get("sources", {}).get("arxiv", {}).get("keywords", {})
        if isinstance(arxiv_keywords, dict):
            return list(arxiv_keywords.keys())
        return []

    def should_download_pdfs(self) -> bool:
        """Check if PDFs should be downloaded"""
        return self.config.get("global", {}).get("download_pdfs", True)

    def get_sorting_method(self) -> Dict:
        """Get sorting configuration"""
        return self.config.get("sorting", {"method": "date", "order": "descending"})
