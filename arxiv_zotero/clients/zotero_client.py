import logging
import time
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Any

import requests
from pyzotero import zotero

logger = logging.getLogger(__name__)

# Zotero API constants
# Zotero API 限制: 每 10 分钟 100 次请求
ZOTERO_RATE_LIMIT_WINDOW = 600  # 10分钟（秒）
ZOTERO_RATE_LIMIT_MAX_REQUESTS = 100  # 最大请求数
ZOTERO_RATE_LIMIT_THRESHOLD = 90  # 90% 限制时开始等待
ZOTERO_MIN_REQUEST_INTERVAL = 6.0  # 最小请求间隔（秒）
ZOTERO_RATE_LIMIT_BUFFER = 5  # 额外缓冲时间（秒）

# 缓存常量
CACHE_TTL_SECONDS = 300  # 缓存有效期 5 分钟（秒）
LOOKUP_CACHE_MAX_SIZE = 1000  # 通用查重缓存最大条目数
LOOKUP_CACHE_EVICT_SIZE = 200  # 缓存满时删除的条目数


class ZoteroAPIError(Exception):
    """Custom exception for Zotero API errors"""

    pass


class ZoteroClient:
    """Class to handle all Zotero-specific operations"""

    def __init__(self, library_id: str, api_key: str, collection_key: str = None):
        """
        Initialize the Zotero client

        Args:
            library_id: Zotero library identifier
            api_key: Zotero API key
            collection_key: Optional collection key to add items to
        """
        self.zot = zotero.Zotero(library_id, "user", api_key)
        self.collection_key = collection_key

        # Configure HTTP session for better performance
        self.session = requests.Session()
        self.session.mount(
            "https://",
            requests.adapters.HTTPAdapter(max_retries=3, pool_connections=10, pool_maxsize=20),
        )

        # ========== 优化: 缓存和速率限制 ==========
        # arXiv ID 缓存,避免重复请求
        self._arxiv_id_cache: Dict[str, str] = {}  # {arxiv_id: item_key}
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = CACHE_TTL_SECONDS  # 缓存有效期 5 分钟

        # 通用查找缓存 (TTL 缓存) - 缓存最近 1000 次查重结果
        self._lookup_cache: Dict[str, Optional[str]] = {}
        self._lookup_cache_hits = 0
        self._lookup_cache_misses = 0

        # API 请求统计
        self._request_count = 0
        self._start_time = time.time()

        # 速率限制保护 (Zotero 限制: 每 10 分钟 100 次)
        # 即: 每 6 秒 1 次请求
        self.request_times = deque(maxlen=ZOTERO_RATE_LIMIT_MAX_REQUESTS)
        self.min_request_interval = ZOTERO_MIN_REQUEST_INTERVAL  # 最小请求间隔

        if collection_key:
            self._validate_collection()

    def _rate_limit(self):
        """
        速率限制保护,确保不超过 Zotero API 限制

        Zotero 限制: 每 10 分钟 100 次请求
        实现: 如果接近限制,自动等待
        """
        now = time.time()

        # 移除 ZOTERO_RATE_LIMIT_WINDOW 秒前的请求记录
        while self.request_times and now - self.request_times[0] > ZOTERO_RATE_LIMIT_WINDOW:
            self.request_times.popleft()

        # 如果达到 ZOTERO_RATE_LIMIT_THRESHOLD 次请求(90% 限制),开始等待
        if len(self.request_times) >= ZOTERO_RATE_LIMIT_THRESHOLD:
            sleep_time = ZOTERO_RATE_LIMIT_WINDOW - (now - self.request_times[0]) + ZOTERO_RATE_LIMIT_BUFFER  # 额外缓冲
            if sleep_time > 0:
                logger.warning(
                    f"接近 Zotero API 速率限制 ({len(self.request_times)}/{ZOTERO_RATE_LIMIT_MAX_REQUESTS}), "
                    f"等待 {sleep_time:.1f} 秒..."
                )
                time.sleep(sleep_time)

        # 如果两次请求间隔太短,等待
        if self.request_times:
            time_since_last = now - self.request_times[-1]
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)

    def _track_request(self):
        """记录 API 请求,用于统计和速率限制"""
        self._request_count += 1
        self.request_times.append(time.time())

        # 每 50 次请求输出一次统计
        if self._request_count % 50 == 0:
            elapsed = time.time() - self._start_time
            rate = self._request_count / elapsed if elapsed > 0 else 0
            logger.info(
                f"API 请求统计: {self._request_count} 次, 耗时 {elapsed:.1f} 秒, 平均速率 {rate:.2f} 次/秒"
            )

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._cache_timestamp is None:
            return False
        return (time.time() - self._cache_timestamp) < self._cache_ttl

    def _refresh_arxiv_id_cache(self):
        """刷新 arXiv ID 缓存"""
        try:
            logger.info("刷新 arXiv ID 缓存...")
            self._rate_limit()  # 速率限制

            results = self.zot.items(sort="dateAdded", direction="desc", limit=500)

            # 构建缓存: {arxiv_id: item_key}
            self._arxiv_id_cache = {}
            for item in results:
                item_data = item.get("data", item) if isinstance(item, dict) else item
                arxiv_id = item_data.get("archiveLocation", "")
                if arxiv_id:
                    self._arxiv_id_cache[arxiv_id.strip()] = item_data.get("key")

            self._cache_timestamp = time.time()
            self._track_request()

            logger.info(f"arXiv ID 缓存已刷新,共 {len(self._arxiv_id_cache)} 条记录")

        except Exception as e:
            logger.error(f"刷新 arXiv ID 缓存失败: {str(e)}")
            # 失败时使用空缓存,避免影响后续操作
            self._arxiv_id_cache = {}
            self._cache_timestamp = None

    def get_api_stats(self) -> Dict[str, Any]:
        """
        获取 API 请求统计信息

        Returns:
            Dict containing:
                - total_requests: 总请求数
                - elapsed_time: 总耗时(秒)
                - rate: 平均速率(请求/秒)
                - cache_size: 缓存条目数
        """
        elapsed = time.time() - self._start_time
        return {
            "total_requests": self._request_count,
            "elapsed_time": elapsed,
            "rate": self._request_count / elapsed if elapsed > 0 else 0,
            "cache_size": len(self._arxiv_id_cache),
        }

    def _validate_collection(self):
        """
        Validate that the specified collection exists

        Raises:
            ValueError: If collection does not exist
        """
        try:
            collections = self.zot.collections()
            if not any(col["key"] == self.collection_key for col in collections):
                raise ValueError(f"Collection {self.collection_key} does not exist")
            logger.info(f"Successfully validated collection {self.collection_key}")
        except Exception as e:
            logger.error(
                f"Failed to validate collection '{self.collection_key}': {str(e)}\n"
                f"Solutions:\n"
                f"  1. Verify the collection key is correct\n"
                f"  2. Check your API key has permission to access this collection\n"
                f"  3. Ensure the collection exists in your Zotero library\n"
                f"Get collection keys: https://www.zotero.org/settings/keys"
            )
            raise

    def create_item(self, template_type: str, metadata: Dict) -> Optional[str]:
        """
        Create a new item in Zotero

        Args:
            template_type: Type of Zotero item ('journalArticle', 'attachment', etc.)
            metadata: Mapped metadata to apply to the template

        Returns:
            Optional[str]: Item key if successful, None otherwise
        """
        try:
            self._rate_limit()  # 速率限制
            template = self.zot.item_template(template_type)
            template.update(metadata)

            response = self.zot.create_items([template])
            self._track_request()  # 统计请求

            if "successful" in response and response["successful"]:
                item_key = list(response["successful"].values())[0]["key"]
                logger.info(f"Successfully created item with key: {item_key}")
                return item_key
            else:
                logger.error(
                    f"Failed to create Zotero item. Response: {response}\n"
                    f"Solutions:\n"
                    f"  1. Check API key permissions: https://www.zotero.org/settings/keys\n"
                    f"  2. Verify metadata format is valid\n"
                    f"  3. Check if you've exceeded API rate limits (100 requests per 10 minutes)\n"
                    f"  4. Ensure network connectivity to Zotero API"
                )
                return None

        except Exception as e:
            logger.error(
                f"Error creating Zotero item: {str(e)}\n"
                f"Solutions:\n"
                f"  1. Verify API key is valid and has write permissions\n"
                f"  2. Check metadata does not contain invalid characters\n"
                f"  3. Ensure you're not exceeding Zotero storage limits"
            )
            raise ZoteroAPIError(f"Failed to create Zotero item: {str(e)}")

    def add_to_collection(self, item_key: str) -> bool:
        """
        Add an item to the specified collection

        Args:
            item_key: Key of the item to add

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.collection_key:
            return True

        try:
            self._rate_limit()  # 速率限制
            item = self.zot.item(item_key)
            success = self.zot.addto_collection(self.collection_key, item)
            self._track_request()  # 统计请求

            if success:
                logger.info(f"Successfully added item {item_key} to collection")
                return True
            else:
                logger.error(f"Failed to add item {item_key} to collection")
                return False

        except Exception as e:
            logger.error(f"Error adding to collection: {str(e)}")
            raise ZoteroAPIError(f"Failed to add item to collection: {str(e)}")

    def upload_attachment(self, parent_key: str, filepath: Path, filename: str) -> bool:
        """
        Upload a file attachment to a Zotero item

        Args:
            parent_key: Key of the parent item
            filepath: Path to the file to upload
            filename: Name to use for the uploaded file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create attachment item template
            attachment = self.zot.item_template("attachment", "imported_file")
            attachment.update(
                {
                    "title": filename,
                    "parentItem": parent_key,
                    "contentType": "application/pdf",
                    "filename": str(filepath),
                }
            )

            # Upload the attachment
            result = self.zot.upload_attachments([attachment])

            # Check if the attachment was created
            if result:
                has_attachment = (
                    len(result.get("success", [])) > 0 or len(result.get("unchanged", [])) > 0
                )
                if has_attachment:
                    logger.info(f"Successfully uploaded attachment for item {parent_key}")
                    return True
                elif len(result.get("failure", [])) > 0:
                    logger.error(f"Failed to upload attachment. Response: {result}")
                    return False
                else:
                    logger.warning(f"Unexpected attachment result: {result}")
                    return False
            else:
                logger.error("No result returned from upload_attachments")
                return False

        except Exception as e:
            logger.error(f"Error uploading attachment: {str(e)}")
            raise ZoteroAPIError(f"Failed to upload attachment: {str(e)}")

    def check_duplicate(
        self, identifier: str, identifier_field: str = "DOI", collection_only: bool = False
    ) -> Optional[str]:
        """
        Check if an item already exists in the library (优化版:使用缓存)

        Args:
            identifier: Value to search for (DOI, arXiv ID, etc.)
            identifier_field: Field to search in (DOI, archiveLocation, etc.)
            collection_only: If True, only search in the specified collection

        Returns:
            Optional[str]: Item key if found, None otherwise

        Note:
            使用缓存机制避免重复 API 请求:
            - 首次调用: 加载最近 500 篇论文到缓存 (1 次 API 请求)
            - 后续调用: 从缓存查找 (0 次 API 请求)
            - 缓存有效期: 5 分钟
            - collection_only: 集合内查重更快 (约0.5-1秒 vs 2-3秒)
        """
        try:
            # 集合内查重模式
            if collection_only and self.collection_key:
                logger.debug(f"使用集合内查重模式 (collection: {self.collection_key})")
                self._rate_limit()
                # 只查询指定集合，限制为100篇（足够快）
                results = self.zot.items(
                    collection=self.collection_key, sort="dateAdded", direction="desc", limit=100
                )
                self._track_request()

                if results:
                    for item in results:
                        item_data = item.get("data", item) if isinstance(item, dict) else item
                        field_value = item_data.get(identifier_field, "")

                        if field_value and str(field_value).strip() == str(identifier).strip():
                            logger.info(
                                f"Found duplicate {identifier_field} '{identifier}' in item {item_data.get('key')} (collection-only)"
                            )
                            return item_data.get("key")

                logger.debug(
                    f"No duplicate found for {identifier_field}='{identifier}' in collection {self.collection_key}"
                )
                return None

            # 全局查重模式（原有逻辑）
            # 只对 archiveLocation 字段使用缓存优化
            if identifier_field == "archiveLocation":
                # 检查缓存是否有效,无效则刷新
                if not self._is_cache_valid():
                    self._refresh_arxiv_id_cache()

                # 从缓存查找
                item_key = self._arxiv_id_cache.get(identifier.strip())
                if item_key:
                    logger.info(
                        f"从缓存找到重复 {identifier_field} '{identifier}' → item {item_key}"
                    )
                return item_key

            # 其他字段使用通用缓存优化
            cache_key = f"{identifier_field}:{identifier}"
            if cache_key in self._lookup_cache:
                # 缓存命中
                self._lookup_cache_hits += 1
                cached_result = self._lookup_cache[cache_key]
                if cached_result:
                    logger.info(
                        f"从通用缓存找到重复 {identifier_field} '{identifier}' → item {cached_result}"
                    )
                else:
                    logger.debug(
                        f"通用缓存确认 {identifier_field} '{identifier}' 不存在 (cache miss)"
                    )
                return cached_result

            # 缓存未命中，查询 API
            self._lookup_cache_misses += 1
            logger.debug(f"通用缓存未命中 ({self._lookup_cache_hits} hits, {self._lookup_cache_misses} misses)")
            self._rate_limit()
            results = self.zot.items(sort="dateAdded", direction="desc", limit=500)
            self._track_request()

            # 更新缓存（限制缓存大小）
            if len(self._lookup_cache) >= LOOKUP_CACHE_MAX_SIZE:
                # 缓存太大，清除最旧的 20%
                keys_to_remove = list(self._lookup_cache.keys())[:LOOKUP_CACHE_EVICT_SIZE]
                for key in keys_to_remove:
                    del self._lookup_cache[key]

            if results:
                for item in results:
                    item_data = item.get("data", item) if isinstance(item, dict) else item
                    field_value = item_data.get(identifier_field, "")

                    if field_value and str(field_value).strip() == str(identifier).strip():
                        logger.info(
                            f"Found duplicate {identifier_field} '{identifier}' in item {item_data.get('key')}"
                        )
                        return item_data.get("key")

            logger.debug(
                f"No duplicate found for {identifier_field}='{identifier}' in recent 500 items"
            )
            return None

        except Exception as e:
            logger.error(f"Error checking for duplicate: {str(e)}")
            return None

    def delete_item(self, item_key: str) -> bool:
        """
        Delete an item from the library

        Args:
            item_key: Key of the item to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.zot.delete_item(item_key)
            logger.info(f"Successfully deleted item {item_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return False

    def create_collection(self, name: str, parent_collection: str = None) -> Optional[str]:
        """
        Create a new collection

        Args:
            name: Name of the collection
            parent_collection: Optional parent collection key

        Returns:
            Optional[str]: Collection key if successful, None otherwise
        """
        try:
            collections = self.zot.create_collections(
                [{"name": name, "parentCollection": parent_collection}]
            )

            if collections:
                collection_key = collections["successful"]["0"]["key"]
                logger.info(f"Successfully created collection: {collection_key}")
                return collection_key
            return None

        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return None

    def close(self):
        """Cleanup resources"""
        if self.session:
            self.session.close()

    def __del__(self):
        """Cleanup resources on deletion"""
        self.close()
