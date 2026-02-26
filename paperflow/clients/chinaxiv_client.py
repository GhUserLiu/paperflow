"""
ChinaXiv Client for searching and retrieving papers from ChinaXiv
ChinaXiv 客户端：用于从中国科技论文在线搜索和获取论文
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests

from ..core.search_params import ArxivSearchParams

logger = logging.getLogger(__name__)


class ChinaXivClient:
    """Class to handle all ChinaXiv-specific operations"""

    def __init__(self):
        """Initialize the ChinaXivClient"""
        self.base_url = "https://chinaxiv.org"
        self.search_url = f"{self.base_url}/search/search"
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    def _parse_paper_id(self, paper_id: str) -> Dict:
        """
        Parse ChinaXiv paper ID (format: YYYYMM.NNNNN)
        解析 ChinaXiv 论文 ID（格式：年月.序号）
        """
        try:
            # ChinaXiv ID format: 202601.00191
            match = re.match(r"(\d{6})\.(\d+)", paper_id)
            if match:
                year_month, number = match.groups()
                return {"year": year_month[:4], "month": year_month[4:6], "number": number}
        except Exception as e:
            logger.warning(f"Could not parse paper ID {paper_id}: {str(e)}")
        return {}

    async def _prepare_chinaxiv_metadata(self, paper_data: Dict) -> Optional[Dict]:
        """
        Prepare metadata from ChinaXiv paper data
        从 ChinaXiv 论文数据准备元数据
        """
        try:
            # Extract ChinaXiv ID from URL or data
            chinaxiv_id = paper_data.get("id", "") or paper_data.get("chinaxiv_id", "")
            chinaxiv_url = paper_data.get("url", "")

            # Extract authors
            authors_list = paper_data.get("authors", [])
            if isinstance(authors_list, str):
                authors_list = [a.strip() for a in authors_list.split(",")]
            elif not isinstance(authors_list, list):
                authors_list = []

            # Extract publication date
            published_date = paper_data.get("publishDate") or paper_data.get("published_date")
            if published_date:
                try:
                    if isinstance(published_date, str):
                        published_date = datetime.strptime(published_date.split("T")[0], "%Y-%m-%d")
                except Exception as e:
                    logger.warning(f"Could not parse date {published_date}: {str(e)}")
                    published_date = datetime.now()
            else:
                published_date = datetime.now()

            # Build metadata dictionary compatible with arXiv format
            return {
                "title": paper_data.get("title", ""),
                "abstract": paper_data.get("abstract", "") or paper_data.get("summary", ""),
                "authors": authors_list,
                "published": (
                    published_date.strftime("%Y-%m-%d")
                    if isinstance(published_date, datetime)
                    else str(published_date)
                ),
                "chinaxiv_id": chinaxiv_id,
                "chinaxiv_url": chinaxiv_url or f"{self.base_url}/home.htm?id={chinaxiv_id}",
                "pdf_url": paper_data.get("pdf_url", ""),
                "primary_category": paper_data.get("category", ""),
                "categories": (
                    [paper_data.get("category", "")] if paper_data.get("category") else []
                ),
                "doi": paper_data.get("doi", ""),
                "keywords": paper_data.get("keywords", []),
                "source": "chinaxiv",  # 标识来源
            }
        except Exception as e:
            logger.error(f"Error preparing ChinaXiv metadata: {str(e)}")
            return None

    def search_chinaxiv(self, search_params: ArxivSearchParams) -> List[Dict]:
        """
        Search ChinaXiv using provided search parameters
        使用提供的搜索参数搜索 ChinaXiv
        """
        try:
            keywords = " ".join(search_params.keywords) if search_params.keywords else ""

            logger.info(f"Executing ChinaXiv search with keywords: {keywords}")

            papers = []

            # Build search request
            # ChinaXiv search endpoint parameters (based on website analysis)
            params = {
                "key": keywords,
                "page": 1,
                "size": min(search_params.max_results, 50),  # Limit per page
            }

            # Add date filters if specified
            if search_params.start_date:
                params["startDate"] = search_params.start_date.strftime("%Y-%m-%d")
            if search_params.end_date:
                params["endDate"] = search_params.end_date.strftime("%Y-%m-%d")

            try:
                # Attempt to use API (ChinaXiv requires POST method)
                response = self.session.post(
                    f"{self.base_url}/api/search", json=params, timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("success") and data.get("data"):
                        # Parse API response
                        results = (
                            data["data"].get("list", [])
                            if isinstance(data["data"], dict)
                            else data["data"]
                        )

                        for item in results[: search_params.max_results]:
                            paper_data = self._parse_api_result(item)
                            if paper_data:
                                # Apply filters
                                paper_meta = asyncio.run(
                                    self._prepare_chinaxiv_metadata(paper_data)
                                )
                                if paper_meta:
                                    if self._apply_filters(paper_meta, search_params):
                                        papers.append(paper_meta)
                    else:
                        logger.warning(
                            f"ChinaXiv API returned error: {data.get('message', 'Unknown error')}"
                        )
                        papers = self._fallback_web_search(keywords, search_params)

                else:
                    logger.warning(f"ChinaXiv API returned status {response.status_code}")
                    papers = self._fallback_web_search(keywords, search_params)

            except Exception as api_error:
                logger.warning(
                    f"ChinaXiv API search failed: {str(api_error)}, trying web scraping..."
                )
                papers = self._fallback_web_search(keywords, search_params)

            # Apply date filter and limit results
            papers = papers[: search_params.max_results]
            logger.info(f"Found {len(papers)} papers from ChinaXiv matching the criteria")
            return papers

        except Exception as e:
            logger.error(f"Error searching ChinaXiv: {str(e)}")
            return []

    def _parse_api_result(self, item: Dict) -> Dict:
        """Parse API result item into standard format"""
        return {
            "id": item.get("id") or item.get("chinaxivId"),
            "title": item.get("title") or item.get("resourceName"),
            "abstract": item.get("abstract") or item.get("description"),
            "authors": item.get("authors") or item.get("author"),
            "publishDate": item.get("publishDate") or item.get("publishTime"),
            "pdf_url": item.get("pdfUrl") or item.get("pdfUrl"),
            "category": item.get("discipline") or item.get("category"),
            "doi": item.get("doi"),
            "keywords": item.get("keywords") or [],
            "url": item.get("url") or f"{self.base_url}/home.htm?id={item.get('id')}",
        }

    def _fallback_web_search(self, keywords: str, search_params: ArxivSearchParams) -> List[Dict]:
        """
        Fallback to web scraping if API fails
        如果 API 失败，回退到网页抓取
        """
        logger.info("Attempting web scraping as fallback...")
        papers = []

        try:
            # Use BeautifulSoup to parse the HTML search results page
            from bs4 import BeautifulSoup

            # Construct search URL (ChinaXiv uses /user/search.htm)
            # 需要URL编码关键词
            from urllib.parse import quote
            encoded_keywords = quote(keywords)
            search_url = f"{self.base_url}/user/search.htm?searchWords={encoded_keywords}"

            logger.info(f"Fetching search page: {search_url}")
            response = self.session.get(search_url, timeout=30)

            if response.status_code != 200:
                logger.warning(f"Failed to fetch search page: {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all paper entries in the search results
            # ChinaXiv search results are typically in table or div format
            paper_entries = soup.find_all('div', class_='search-result-item')
            if not paper_entries:
                # Try alternative selectors
                paper_entries = soup.find_all('tr', class_='search-item')
            if not paper_entries:
                # Try to find any div with data-id attribute
                paper_entries = soup.find_all('div', attrs={'data-id': True})

            logger.info(f"Found {len(paper_entries)} paper entries on page")

            for entry in paper_entries[: search_params.max_results]:
                try:
                    paper_data = self._parse_html_entry(entry)
                    if paper_data:
                        # Prepare metadata
                        paper_meta = asyncio.run(
                            self._prepare_chinaxiv_metadata(paper_data)
                        )
                        if paper_meta and self._apply_filters(paper_meta, search_params):
                            papers.append(paper_meta)
                            logger.info(f"Successfully parsed paper: {paper_meta.get('title', 'Unknown')[:50]}")
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {str(e)}")
                    continue

            logger.info(f"Web scraping found {len(papers)} valid papers")

        except ImportError:
            logger.warning("BeautifulSoup not available. Install with: pip install beautifulsoup4")
        except Exception as e:
            logger.error(f"Web scraping failed: {str(e)}")

        return papers

    def _parse_html_entry(self, entry) -> Optional[Dict]:
        """
        Parse a single HTML entry into paper data
        解析单个 HTML 条目为论文数据
        """
        try:
            # Extract paper ID
            data_id = entry.get('data-id') or entry.find('a', href=True).get('href', '').split('=')[-1] if entry.find('a', href=True) else None

            # Extract title
            title_elem = entry.find('h3') or entry.find('h4') or entry.find('a', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Extract abstract
            abstract_elem = entry.find('div', class_='abstract') or entry.find('p', class_='description')
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''

            # Extract authors
            authors_elem = entry.find('div', class_='authors') or entry.find('span', class_='author')
            authors = []
            if authors_elem:
                authors = [a.get_text(strip=True) for a in authors_elem.find_all('span') if a.get_text(strip=True)]

            # Extract PDF URL
            pdf_elem = entry.find('a', href=True)
            pdf_url = ''
            if pdf_elem and 'pdf' in pdf_elem.get('href', '').lower():
                pdf_url = pdf_elem.get('href', '')
                if not pdf_url.startswith('http'):
                    pdf_url = f"{self.base_url}{pdf_url}"

            # Extract publication date
            date_elem = entry.find('span', class_='publish-date') or entry.find('time')
            publish_date = date_elem.get('datetime') or date_elem.get_text(strip=True) if date_elem else None

            # Extract DOI
            doi_elem = entry.find('span', class_='doi') or entry.find('a', href=lambda x: x and 'doi.org' in x)
            doi = doi_elem.get_text(strip=True) if doi_elem else ''
            if doi_elem and isinstance(doi_elem, dict):
                doi = doi_elem.get('content', '')

            # Extract URL
            url_elem = entry.find('a', href=True)
            url = url_elem.get('href', '') if url_elem else ''
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"

            return {
                'id': data_id,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'publishDate': publish_date,
                'pdf_url': pdf_url,
                'doi': doi,
                'url': url,
                'chinaxiv_id': data_id,
            }
        except Exception as e:
            logger.warning(f"Failed to parse HTML entry: {str(e)}")
            return None

    def _apply_filters(self, paper: Dict, search_params: ArxivSearchParams) -> bool:
        """Apply date and content type filters"""
        # Date filter
        if search_params.start_date or search_params.end_date:
            try:
                pub_date = datetime.strptime(paper["published"], "%Y-%m-%d")

                if search_params.start_date:
                    if pub_date < search_params.start_date:
                        return False

                if search_params.end_date:
                    if pub_date > search_params.end_date:
                        return False
            except Exception as e:
                logger.warning(f"Could not parse date for filtering: {str(e)}")

        return True

    def download_pdf(self, pdf_url: str, save_path: str) -> bool:
        """
        Download PDF from ChinaXiv
        从 ChinaXiv 下载 PDF
        """
        try:
            response = self.session.get(pdf_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Successfully downloaded PDF from {pdf_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to download PDF from {pdf_url}: {str(e)}")
            return False
