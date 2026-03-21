import logging
import random
import requests

REQUEST_TIMEOUT = 15

logger = logging.getLogger("scrapers")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


def get_headers(rotate_ua=True):
    ua = random.choice(USER_AGENTS) if rotate_ua else USER_AGENTS[0]
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def safe_request(url, proxy_manager=None, rotate_ua=True, method="get", **kwargs):
    """Make a request with proxy rotation, retry logic, and logging."""
    headers = get_headers(rotate_ua)
    proxy_dict = proxy_manager.get_proxy_dict() if proxy_manager else None

    for attempt in range(2):
        try:
            if method == "get":
                resp = requests.get(
                    url, headers=headers, proxies=proxy_dict,
                    timeout=REQUEST_TIMEOUT, **kwargs,
                )
            else:
                resp = requests.post(
                    url, headers=headers, proxies=proxy_dict,
                    timeout=REQUEST_TIMEOUT, **kwargs,
                )
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
            if proxy_manager and proxy_dict:
                proxy_manager.mark_dead(proxy_dict)
                proxy_dict = proxy_manager.get_proxy_dict()
                continue
            return None
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            logger.warning(f"HTTP {status} from {url} (attempt {attempt + 1})")
            if proxy_manager and proxy_dict:
                proxy_manager.mark_dead(proxy_dict)
                proxy_dict = proxy_manager.get_proxy_dict()
                continue
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error to {url} (attempt {attempt + 1})")
            if proxy_manager and proxy_dict:
                proxy_manager.mark_dead(proxy_dict)
                proxy_dict = proxy_manager.get_proxy_dict()
                continue
            return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {type(e).__name__}: {e}")
            if proxy_manager and proxy_dict:
                proxy_manager.mark_dead(proxy_dict)
                proxy_dict = proxy_manager.get_proxy_dict()
                continue
            return None
    return None
