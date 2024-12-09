import requests
import pandas as pd
import urllib.parse as urlparse
from typing import List, Dict, Set

import ssl
import certifi
import aiohttp
import asyncio
import platform
from bs4 import BeautifulSoup
from aiohttp import ClientTimeout
from fake_useragent import UserAgent
from aiohttp_retry import RetryClient, ExponentialRetry

class NewsService():

    def __init__(self, bing_api_key: str):
        self.bing_api_key = bing_api_key
        self.bing_session = requests.Session()

        self.bing_base_url = "https://api.bing.microsoft.com/v7.0/news/search"
        self.bing_session.headers.update({
            'Ocp-Apim-Subscription-Key': self.bing_api_key
        })

        self.fast_news_scraper = self.FastNewsScraper(max_concurrent=10, timeout=10)

    def search_bing_news(self, queries: List[str], count: int = 5) -> List[str]:
        """
        Search news articles using Bing News API for multiple queries
        
        Args:
            queries: List of search terms
            count: Number of results to return per query (max 100)
            
        Returns:
            List of unique URLs from all search results
        """
        all_urls = []
        all_bing_results = []
        
        for query in queries:
            params = {
                'q': f'{query} -site:msn.com',
                'count': min(count, 100),
                'freshness': 'Month' #Day
            }
            
            response = self.bing_session.get(self.bing_base_url, params=params)
            bing_results = response.json()
            
            # Extract URLs from current query results and extend all_results
            current_urls = [item.get('url') for item in bing_results.get('value', [])]
            all_urls.extend(current_urls)
            all_bing_results.extend(bing_results.get('value', []))

        # print('search_bing_news urls:')
        # print(all_urls)

        # print('all_bing_results:')
        # print(all_bing_results)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            scrapping_results = loop.run_until_complete(self.fast_news_scraper.scrape_urls(all_urls))
        finally:
            if platform.system() != 'Windows':  # Windows has issues with loop cleanup
                loop.close()
        
        # print('run_until_complete count:')
        # print(len(scrapping_results))

        search_bing_news_final_result = [item for item in scrapping_results if item['text'] and item['text'].strip()]

        # Create a lookup dictionary for faster access to names by URL
        url_to_name = {mapping['url']: mapping['name'] for mapping in all_bing_results}

        # Update the title of articles based on the mapping
        for article in search_bing_news_final_result:
            if article['url'] in url_to_name:
                article['title'] = url_to_name[article['url']]

        # print('search_bing_news_final_result')
        # print(len(search_bing_news_final_result))
        return search_bing_news_final_result
    
    class FastNewsScraper:
        """Asynchronous news content scraper optimized for speed"""
        
        def __init__(self, max_concurrent: int = 50, timeout: int = 10):
            self.max_concurrent = max_concurrent
            self.timeout = ClientTimeout(total=timeout)
            self.ua = UserAgent()
            self.seen_urls: Set[str] = set()
            
            # Configure logging
            # logging.basicConfig(level=logging.INFO)
            # self.logger = logging.getLogger(__name__)
            
            # Setup SSL context
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())

        def _get_random_headers(self) -> Dict[str, str]:
            """Generate random headers for each request"""
            return {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }

        async def __extract_content(self, html: str) -> Dict[str, str]:
            """Extract content from HTML using BeautifulSoup with minimal parsing"""
            try:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Quick removal of unnecessary elements
                for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'aside']):
                    tag.decompose()
                
                # Fast content extraction using common patterns
                content = {
                    'title': '',
                    'text': '',
                    'metadata': {}
                }
                
                # Quick title extraction
                title_tag = (
                    soup.find('h1') or 
                    soup.find('meta', property='og:title') or
                    soup.find('title')
                )
                if title_tag:
                    content['title'] = title_tag.get_text() if hasattr(title_tag, 'get_text') else title_tag.get('content', '')
                
                # Quick main content extraction
                article_tag = (
                    soup.find('article-content') or
                    soup.find('article') or
                    soup.find('body', class_=['article-body']) or
                    soup.find('div', class_=['article-content', 'story-content', 'post-content']) or
                    soup.find('div', {'itemprop': 'articleBody'})
                )
                
                if article_tag:
                    # Extract text efficiently
                    paragraphs = article_tag.find_all('p')
                    content['text'] = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                
                return content
                
            except Exception as e:
                self.logger.error(f"Content extraction error: {str(e)}")
                return {'title': '', 'text': '', 'metadata': {}}

        async def __fetch_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, str]:
            """Fetch and process a single URL"""
            try:
                retry_options = ExponentialRetry(attempts=2)
                retry_client = RetryClient(client_session=session, retry_options=retry_options)
                
                async with retry_client.get(
                    url,
                    headers=self._get_random_headers(),
                    timeout=self.timeout,
                    ssl=self.ssl_context
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        content = await self.__extract_content(html)
                        content['url'] = url
                        content['status'] = 'success'
                        return content
                    else:
                        return {'url': url, 'status': 'error', 'error': f'HTTP {response.status}'}
                        
            except asyncio.TimeoutError:
                return {'url': url, 'status': 'error', 'error': 'timeout'}
            except Exception as e:
                return {'url': url, 'status': 'error', 'error': str(e)}

        async def scrape_urls(self, urls: List[str]) -> List[Dict[str, str]]:
            """
            Scrape multiple URLs concurrently
            
            Args:
                urls: List of URLs to scrape
                
            Returns:
                List of dictionaries containing scraped content
            """
            # Remove duplicates and already seen URLs
            unique_urls = list(set(urls) - self.seen_urls)
            self.seen_urls.update(unique_urls)
            
            if not unique_urls:
                return []
            
            # Create connection pool
            conn = aiohttp.TCPConnector(
                limit=self.max_concurrent,
                ttl_dns_cache=300,
                ssl=self.ssl_context
            )
            
            async with aiohttp.ClientSession(connector=conn) as session:
                tasks = [
                    self.__fetch_url(session, url)
                    for url in unique_urls
                ]
                
                # Use semaphore to limit concurrent requests
                semaphore = asyncio.Semaphore(self.max_concurrent)
                async def bounded_fetch(task):
                    async with semaphore:
                        return await task
                
                # Gather results with timeout
                results = await asyncio.gather(
                    *(bounded_fetch(task) for task in tasks),
                    return_exceptions=True
                )
                
                # Filter out failures and exceptions
                valid_results = [
                    result for result in results
                    if isinstance(result, dict) and result.get('status') == 'success'
                ]
                
                return valid_results