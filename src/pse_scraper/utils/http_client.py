"""
HTTP request utilities for PSE data scraping.
"""

import time
import random
import logging
from typing import Dict, List, Optional
import requests
from requests.exceptions import RequestException, ProxyError


class HTTPClient:
    """HTTP client with retry logic and proxy support."""
    
    def __init__(self, use_proxies: bool = False, proxies: List[str] = None):
        """
        Initialize HTTP client.
        
        Args:
            use_proxies: Whether to use proxy rotation
            proxies: List of proxy addresses in format "ip:port"
        """
        self.session = requests.Session()
        self.use_proxies = use_proxies
        self.proxies = proxies or []
        self.logger = logging.getLogger(__name__)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list."""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    
    def make_request(
        self,
        url: str,
        method: str = "get",
        params: Dict = None,
        data: Dict = None,
        retries: int = 3,
        timeout: int = 30,
    ) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling and retry logic.

        Args:
            url: Target URL
            method: HTTP method (get/post)
            params: URL parameters
            data: Data for POST request
            retries: Number of retries on failure
            timeout: Timeout in seconds

        Returns:
            Response object if successful, None if failed
        """
        for attempt in range(retries):
            try:
                proxy = self.get_random_proxy() if self.use_proxies else None
                response = self.session.request(
                    method,
                    url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    proxies=proxy,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response

            except ProxyError:
                self.logger.warning(f"Proxy error on attempt {attempt + 1}")
                if proxy and proxy["http"] in self.proxies:
                    self.proxies.remove(proxy["http"])

            except RequestException as e:
                self.logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return None

            time.sleep(random.uniform(1, 3))  # Random delay between retries

        return None
