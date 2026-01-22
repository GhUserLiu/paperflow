import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from ..clients.zotero_client import ZoteroAPIError

logger = logging.getLogger(__name__)


class PaperProcessor:
    """Class to handle the processing of individual papers"""

    def __init__(self, zotero_client, metadata_mapper, pdf_manager, summarizer, config):
        """
        Initialize the paper processor

        Args:
            zotero_client: Instance of ZoteroClient
            metadata_mapper: Instance of MetadataMapper
            pdf_manager: Instance of PDFManager
            summarizer: Instance of PaperSummarizer
            config: Application configuration dict
        """
        self.zotero_client = zotero_client
        self.metadata_mapper = metadata_mapper
        self.pdf_manager = pdf_manager
        self.summarizer = summarizer
        self.config = config
        self.collection_key = zotero_client.collection_key
        self.collection_only_dupcheck = False  # 默认全局查重

    def set_collection_only_dupcheck(self, enabled: bool):
        """
        Set whether to use collection-only duplicate checking

        Args:
            enabled: True to check duplicates only in the target collection
        """
        self.collection_only_dupcheck = enabled
        logger.info(f"Collection-only duplicate check: {'enabled' if enabled else 'disabled'}")

    def create_zotero_item(self, paper: Dict) -> Optional[str]:
        """Create a Zotero item from paper metadata"""
        try:
            mapped_data = self.metadata_mapper.map_metadata(paper)
            return self.zotero_client.create_item("journalArticle", mapped_data)
        except ZoteroAPIError as e:
            logger.error(f"Error creating Zotero item: {str(e)}")
            return None

    def add_to_collection(self, item_key: str) -> bool:
        """Add item to collection if collection key is specified"""
        try:
            return self.zotero_client.add_to_collection(item_key)
        except ZoteroAPIError as e:
            logger.error(f"Error adding to collection: {str(e)}")
            return False

    async def process_paper(self, paper: Dict, download_pdfs: bool = True) -> bool:
        """
        Process a single paper asynchronously

        Args:
            paper: Dictionary containing paper metadata
            download_pdfs: Whether to download and attach PDFs

        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Check for duplicate using paper ID (arXiv ID or ChinaXiv ID)
            # 使用论文 ID 检查重复（arXiv ID 或 ChinaXiv ID）
            # Global search across all collections
            # 全局搜索所有集合

            # Get the appropriate ID based on source
            paper_source = paper.get("source", "arxiv")
            paper_id = None
            identifier_field = None

            if paper_source == "chinaxiv":
                paper_id = paper.get("chinaxiv_id")
                identifier_field = "extra"  # ChinaXiv ID stored in extra field
            else:
                paper_id = paper.get("arxiv_id")
                identifier_field = "archiveLocation"  # arXiv ID stored in archiveLocation

            if paper_id:
                existing_item_key = self.zotero_client.check_duplicate(
                    identifier=paper_id,
                    identifier_field=identifier_field,
                    collection_only=self.collection_only_dupcheck,
                )
                if existing_item_key:
                    dup_type = "collection-only" if self.collection_only_dupcheck else "global"
                    logger.info(
                        f"Paper {paper_id} ({paper_source}) already exists in library ({dup_type}, item: {existing_item_key}), skipping"
                    )
                    return (
                        # Return True to indicate successful handling (skipped
                        # as duplicate)
                        True
                    )

            logger.info(f"Processing paper: {paper_id if paper_id else 'unknown'} ({paper_source})")

            # Create main Zotero item
            item_key = self.create_zotero_item(paper)
            if not item_key:
                logger.error("Failed to create main Zotero item")
                return False

            # Add to collection if specified
            if self.collection_key and not self.add_to_collection(item_key):
                logger.error(f"Failed to add item {item_key} to collection")
                return False

            # Handle PDF attachment if requested
            if download_pdfs:
                try:
                    # Download PDF
                    pdf_path, filename = await self.pdf_manager.download_pdf(
                        url=paper["pdf_url"], title=paper["title"]
                    )

                    if not pdf_path or not filename:
                        logger.error("Failed to download PDF")
                        return False

                    # Create and upload attachment
                    attachment_template = self.zotero_client.zot.item_template(
                        "attachment", "imported_file"
                    )
                    attachment_template.update(
                        self.pdf_manager.prepare_attachment_template(
                            filename=filename, parent_item=item_key, filepath=pdf_path
                        )
                    )

                    # Upload the attachment
                    result = self.zotero_client.zot.upload_attachments([attachment_template])

                    if not result:
                        logger.error("No result returned from upload_attachments")
                        return False

                    # Check attachment creation status
                    has_attachment = (
                        len(result.get("success", [])) > 0 or len(result.get("unchanged", [])) > 0
                    )

                    if not has_attachment:
                        if len(result.get("failure", [])) > 0:
                            logger.error(f"Failed to upload attachment. Response: {result}")
                        else:
                            logger.warning(f"Unexpected attachment result: {result}")
                        return False

                    logger.info(f"Successfully processed PDF attachment for item {item_key}")

                    if self.summarizer and self.config.get("summarizer", {}).get("enabled"):
                        await self.summarizer.summarize(pdf_path, self.zotero_client, item_key)

                except Exception as e:
                    logger.error(f"Error in PDF processing: {str(e)}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error processing paper: {str(e)}")
            return False
