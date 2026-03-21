import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .helpers import USER_AGENTS

FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]


class ProxyManager:
    def __init__(self, mode="none", custom_proxies=None):
        self._mode = mode
        self._proxies: list[str] = []
        self._dead: set[str] = set()
        self._index = 0
        self._lock = threading.Lock()
        if custom_proxies:
            if isinstance(custom_proxies, str):
                raw = [p.strip() for p in custom_proxies.replace(",", "\n").split("\n") if p.strip()]
            elif isinstance(custom_proxies, list):
                raw = [p.strip() for p in custom_proxies if p.strip()]
            else:
                raw = []
            for p in raw:
                addr = p
                if addr.startswith("http://"):
                    addr = addr[7:]
                elif addr.startswith("https://"):
                    addr = addr[8:]
                if addr:
                    self._proxies.append(addr)

    @property
    def mode(self):
        return self._mode

    @property
    def proxy_count(self):
        return len(self._proxies)

    @property
    def alive_count(self):
        return len(self._proxies) - len(self._dead)

    def get_proxy_dict(self):
        if self._mode == "none" or not self._proxies:
            return None
        with self._lock:
            attempts = 0
            while attempts < len(self._proxies):
                proxy = self._proxies[self._index % len(self._proxies)]
                self._index += 1
                attempts += 1
                if proxy not in self._dead:
                    if not proxy.startswith("http://") and not proxy.startswith("https://"):
                        proxy = "http://" + proxy
                    return {"http": proxy, "https": proxy}
        return None

    def mark_dead(self, proxy_dict):
        if proxy_dict:
            seen = set()
            for val in proxy_dict.values():
                addr = val
                if addr.startswith("http://"):
                    addr = addr[7:]
                elif addr.startswith("https://"):
                    addr = addr[8:]
                if addr not in seen:
                    seen.add(addr)
                    self._dead.add(addr)
