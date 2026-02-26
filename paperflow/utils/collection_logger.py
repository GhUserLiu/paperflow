"""Collection logger for generating and uploading log files to Zotero"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CollectionLogger:
    """Generate and upload collection logs to Zotero"""

    # Log collection key in Zotero
    LOG_COLLECTION_KEY = "IBZ5WVQU"  # 0-日志集合

    def __init__(self, zotero_client):
        """
        Initialize the collection logger

        Args:
            zotero_client: ZoteroClient instance
        """
        self.zotero_client = zotero_client
        self.start_time = None
        self.stats = {
            "successful": 0,
            "failed": 0,
            "duplicates": 0,
            "categories": {},
            "sources": {},
        }

    def start_timer(self):
        """Start the collection timer"""
        self.start_time = datetime.now()

    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "N/A"
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours} 小时 {minutes} 分钟 {seconds} 秒"
        elif minutes > 0:
            return f"{minutes} 分钟 {seconds} 秒"
        else:
            return f"{seconds} 秒"

    def generate_filename(self, mode: str = "auto") -> str:
        """
        Generate log filename

        Args:
            mode: "auto" or "manual"

        Returns:
            Filename like "Auto_Log_20260124_080000.txt"
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{mode.capitalize()}_Log_{timestamp}.txt"

    def generate_auto_log(
        self,
        category_results: Dict[str, Dict],
        time_filter_hours: int,
        is_bilingual: bool = False,
    ) -> str:
        """
        Generate log content for auto mode

        Args:
            category_results: Dict mapping category to stats
                {
                    "category": {
                        "successful": int,
                        "failed": int,
                        "duplicates": int,
                        "total_found": int,
                        "openalex_used": bool,
                    }
                }
            time_filter_hours: Time filter in hours
            is_bilingual: Whether bilingual mode was used

        Returns:
            Log content as string
        """
        lines = []

        # Header
        lines.append("=" * 50)
        lines.append("ArXiv 云端模式日志")
        lines.append("Cloud Mode Collection Log")
        lines.append("=" * 50)

        # Timestamp
        now = datetime.now()
        utc_time = now.utcnow()
        lines.append(f"执行时间: {now.strftime('%Y-%m-%d %H:%M:%S')} 本地")
        lines.append(f"         {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"时间范围: 过去 {time_filter_hours} 小时")
        lines.append(f"模式: {'双语模式 (arXiv + ChinaXiv)' if is_bilingual else '标准模式'}")

        # Calculate totals
        total_successful = sum(s["successful"] for s in category_results.values())
        total_failed = sum(s["failed"] for s in category_results.values())
        total_duplicates = sum(s["duplicates"] for s in category_results.values())
        total_processed = total_successful + total_failed

        lines.append("")
        lines.append("-" * 50)
        lines.append("总计统计")
        lines.append("-" * 50)
        lines.append(f"成功保存: {total_successful} 篇")
        lines.append(f"处理失败: {total_failed} 篇")
        lines.append(f"已存在(跳过): {total_duplicates} 篇")
        lines.append(f"总处理数: {total_processed} 篇")

        # Category details
        lines.append("")
        lines.append("-" * 50)
        lines.append("分类详情")
        lines.append("Category Details")
        lines.append("-" * 50)

        category_order = ["general", "communication", "perception", "control", "security"]
        category_names = {
            "general": "GENERAL (集合: LRML5CDJ)",
            "communication": "COMMUNICATION (集合: 3E4NFDPR)",
            "perception": "PERCEPTION (集合: 8CQV3SDV)",
            "control": "CONTROL (集合: 8862N8CE)",
            "security": "SECURITY (集合: S97HI5KX)",
        }

        for idx, category in enumerate(category_order):
            if category not in category_results:
                continue

            stats = category_results[category]
            lines.append(f"\n{idx + 1}. {category_names[category].upper()}")
            lines.append(f"   检索到: {stats['total_found']} 篇")

            if stats.get("openalex_used"):
                lines.append(f"   启用 OpenAlex 排序: 是")

            lines.append(f"   保存成功: {stats['successful']} 篇")
            lines.append(f"   已存在(跳过): {stats['duplicates']} 篇")
            lines.append(f"   失败: {stats['failed']} 篇")

        # Footer
        lines.append("")
        lines.append("=" * 50)
        lines.append("执行完成")
        lines.append(f"Completed at: {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"总耗时: {self.get_elapsed_time()}")
        lines.append("=" * 50)

        return "\n".join(lines)

    def generate_manual_log(
        self,
        keywords: str,
        max_results: int,
        download_pdfs: bool,
        openalex_enabled: bool,
        openalex_stats: Optional[Dict],
        source_stats: Dict[str, Dict],
    ) -> str:
        """
        Generate log content for manual mode

        Args:
            keywords: Search keywords
            max_results: Max results requested
            download_pdfs: Whether PDFs were downloaded
            openalex_enabled: Whether OpenAlex ranking was enabled
            openalex_stats: OpenAlex statistics if enabled
            source_stats: Dict mapping source to stats
                {
                    "arxiv": {"found": int, "successful": int, "duplicates": int, "failed": int},
                    "chinaxiv": {...}
                }

        Returns:
            Log content as string
        """
        lines = []

        # Header
        lines.append("=" * 50)
        lines.append("ArXiv 手动检索日志")
        lines.append("Manual Search Log")
        lines.append("=" * 50)

        # Timestamp
        now = datetime.now()
        utc_time = now.utcnow()
        lines.append(f"执行时间: {now.strftime('%Y-%m-%d %H:%M:%S')} 本地")
        lines.append(f"         {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        # Search configuration
        lines.append("")
        lines.append("-" * 50)
        lines.append("检索配置")
        lines.append("Search Configuration")
        lines.append("-" * 50)
        lines.append(f"关键词: {keywords}")
        lines.append(f"最大结果数: {max_results} 篇")
        lines.append(f"下载 PDF: {'是' if download_pdfs else '否'}")
        lines.append(f"OpenAlex 排序: {'启用' if openalex_enabled else '禁用'}")

        # Calculate totals
        total_found = sum(s["found"] for s in source_stats.values())
        total_successful = sum(s["successful"] for s in source_stats.values())
        total_duplicates = sum(s["duplicates"] for s in source_stats.values())
        total_failed = sum(s["failed"] for s in source_stats.values())

        # Source results
        lines.append("")
        lines.append("-" * 50)
        lines.append("检索结果")
        lines.append("Search Results")
        lines.append("-" * 50)

        for source, stats in source_stats.items():
            source_name = "arXiv" if source == "arxiv" else "ChinaXiv"
            lines.append(f"\n{source_name} 源:")
            lines.append(f"  检索到: {stats['found']} 篇")
            lines.append(f"  保存成功: {stats['successful']} 篇")
            lines.append(f"  已存在(跳过): {stats['duplicates']} 篇")
            lines.append(f"  处理失败: {stats['failed']} 篇")

        # Total statistics
        lines.append("")
        lines.append("-" * 50)
        lines.append("总计统计")
        lines.append("Total Statistics")
        lines.append("-" * 50)
        lines.append(f"总检索到: {total_found} 篇")
        lines.append(f"成功保存: {total_successful} 篇")
        lines.append(f"已存在(跳过): {total_duplicates} 篇")
        lines.append(f"处理失败: {total_failed} 篇")

        # OpenAlex statistics (if enabled)
        if openalex_enabled and openalex_stats:
            lines.append("")
            lines.append("-" * 50)
            lines.append("OpenAlex 排序统计")
            lines.append("OpenAlex Ranking Statistics")
            lines.append("-" * 50)
            lines.append(f"总论文数: {openalex_stats.get('total_papers', 0)}")
            lines.append(
                f"有指标数据: {openalex_stats.get('papers_with_metrics', 0)} "
                f"({openalex_stats.get('coverage', 0):.1f}%)"
            )
            if "avg_cited_by_percentile" in openalex_stats:
                lines.append(f"被引百分位平均: {openalex_stats['avg_cited_by_percentile']:.1f}")
            if "avg_h_index" in openalex_stats:
                lines.append(f"h指数平均: {openalex_stats['avg_h_index']:.1f}")
            if "avg_impact_factor" in openalex_stats:
                lines.append(f"影响因子平均: {openalex_stats['avg_impact_factor']:.1f}")

        # Footer
        lines.append("")
        lines.append("=" * 50)
        lines.append("执行完成")
        lines.append(f"Completed at: {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"总耗时: {self.get_elapsed_time()}")
        lines.append("=" * 50)

        return "\n".join(lines)

    async def upload_to_zotero(self, log_content: str, filename: str):
        """
        Upload log file to Zotero

        Args:
            log_content: Log file content
            filename: Log filename

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(log_content)
                tmp_path = tmp.name

            # Create Zotero note item
            note_template = self.zotero_client.zot.item_template("note")
            note_template["note"] = f"<h1>{filename}</h1><pre>{log_content}</pre>"

            # Create item
            created = self.zotero_client.zot.create_items([note_template])
            if not created or "success" not in created:
                return False

            item_key = created["success"][0]

            # Add to log collection
            if self.LOG_COLLECTION_KEY:
                self.zotero_client.add_to_collection(item_key, self.LOG_COLLECTION_KEY)

            # Create attachment for the text file
            attachment_template = self.zotero_client.zot.item_template(
                "attachment", "imported_file"
            )
            attachment_template.update(
                {
                    "parentItem": item_key,
                    "title": filename,
                    "path": tmp_path,
                }
            )

            # Upload attachment
            result = self.zotero_client.zot.upload_attachments([attachment_template])

            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

            return bool(result and len(result.get("success", [])) > 0)

        except Exception as e:
            import logging

            logging.error(f"Failed to upload log to Zotero: {str(e)}")
            return False
