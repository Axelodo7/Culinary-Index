"""
The Culinary Index - Recipe Aggregator & Scraper
Desktop application that searches Food Fusion, SuperChef, Tasty, and the web.
"""

import ctypes
import json
import os
import sys
import random
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import customtkinter as ctk
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Fix Windows taskbar icon BEFORE creating any window
# ---------------------------------------------------------------------------
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("culinaryindex.app.1")

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
APP_NAME = "The Culinary Index"
VERSION = "1.0.0"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

ASSETS_DIR = BASE_DIR / "assets"
SETTINGS_DIR = Path.home() / ".culinary_index"
SETTINGS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

ICON_PATH = ASSETS_DIR / "icon.ico"
ICON_SMALL_PATH = ASSETS_DIR / "icon_small.png"

REQUEST_TIMEOUT = 15

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

FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

# ---------------------------------------------------------------------------
# Settings manager
# ---------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    "sources": {"foodfusion": True, "superchef": True, "tasty": True, "web": True},
    "proxy_mode": "none",
    "custom_proxies": "",
    "rotate_ua": True,
    "window_geometry": "960x720",
}


def load_settings() -> dict:
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged = {**DEFAULT_SETTINGS, **saved}
            merged["sources"] = {**DEFAULT_SETTINGS["sources"], **saved.get("sources", {})}
            return merged
    except Exception:
        pass
    return {**DEFAULT_SETTINGS}


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Proxy Manager
# ---------------------------------------------------------------------------

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
            # Normalize: strip protocol prefix for storage
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

    def fetch_free_proxies(self, status_callback=None) -> int:
        """Fetch and validate free proxies. Returns count of working proxies."""
        raw: set[str] = set()
        for url in FREE_PROXY_SOURCES:
            try:
                r = requests.get(url, timeout=10, headers={"User-Agent": random.choice(USER_AGENTS)})
                for line in r.text.strip().splitlines():
                    line = line.strip()
                    if line and ":" in line:
                        raw.add(line)
            except Exception:
                continue

        if status_callback:
            status_callback(f"Testing {len(raw)} proxies...")

        working: list[str] = []
        def test_proxy(proxy: str) -> str | None:
            try:
                r = requests.head(
                    "https://httpbin.org/ip",
                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                    timeout=5,
                    headers={"User-Agent": random.choice(USER_AGENTS)},
                )
                if r.status_code == 200:
                    return proxy
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=30) as ex:
            futures = {ex.submit(test_proxy, p): p for p in list(raw)[:80]}
            for fut in as_completed(futures):
                result = fut.result()
                if result:
                    working.append(result)
                    if status_callback and len(working) % 5 == 0:
                        status_callback(f"Found {len(working)} working proxies...")

        self._proxies = working[:30]
        self._dead.clear()
        self._index = 0
        return len(self._proxies)

    def get_proxy_dict(self) -> dict | None:
        if self._mode == "none" or not self._proxies:
            return None
        with self._lock:
            attempts = 0
            while attempts < len(self._proxies):
                proxy = self._proxies[self._index % len(self._proxies)]
                self._index += 1
                attempts += 1
                if proxy not in self._dead:
                    # Ensure proper URL format
                    if not proxy.startswith("http://") and not proxy.startswith("https://"):
                        proxy = "http://" + proxy
                    return {"http": proxy, "https": proxy}
        return None

    def mark_dead(self, proxy_dict: dict | None):
        if proxy_dict:
            # Get unique proxy addresses
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


# ---------------------------------------------------------------------------
# Scraper helpers
# ---------------------------------------------------------------------------

def _get_headers(rotate_ua=True) -> dict:
    ua = random.choice(USER_AGENTS) if rotate_ua else USER_AGENTS[0]
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def _safe_request(url, proxy_manager=None, rotate_ua=True, method="get", **kwargs):
    """Make a request with proxy rotation and retry logic."""
    headers = _get_headers(rotate_ua)
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
        except Exception as e:
            if proxy_manager and proxy_dict:
                proxy_manager.mark_dead(proxy_dict)
                proxy_dict = proxy_manager.get_proxy_dict()
                continue
            raise e
    return None


# ---------------------------------------------------------------------------
# Scraper: Food Fusion
# ---------------------------------------------------------------------------

def search_foodfusion(query: str, proxy_manager=None, rotate_ua=True) -> list[dict]:
    results = []
    try:
        url = f"https://www.foodfusion.com/?s={quote_plus(query)}"
        resp = _safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            return results
        soup = BeautifulSoup(resp.text, "html.parser")

        articles = soup.select("article.uk-article")
        for article in articles:
            title_el = article.select_one("h1.uk-article-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = article.select_one("a.uk-button.uk-button-text")
            link = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                if href.startswith("/"):
                    link = "https://www.foodfusion.com" + href
                elif href.startswith("http"):
                    link = href
            if not link:
                link = url
            if title:
                results.append({
                    "title": title,
                    "source": "Food Fusion",
                    "url": link,
                    "prep_time": "",
                })
    except Exception:
        pass
    return results


# ---------------------------------------------------------------------------
# Scraper: SuperChef
# ---------------------------------------------------------------------------

def search_superchef(query: str, proxy_manager=None, rotate_ua=True) -> list[dict]:
    results = []
    try:
        # Try the AJAX autocomplete endpoint first
        ajax_url = f"https://www.superchef.pk/searchFeature?searchFeature={quote_plus(query)}"
        resp = _safe_request(ajax_url, proxy_manager, rotate_ua)
        if resp and resp.text.strip():
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("li")
            for item in items:
                a = item.select_one("a")
                if a:
                    title = a.get_text(strip=True)
                    href = a.get("href", "")
                    if title and href:
                        if not href.startswith("http"):
                            href = "https://www.superchef.pk" + href
                        results.append({
                            "title": title,
                            "source": "SuperChef",
                            "url": href,
                            "prep_time": "",
                        })
            if results:
                return results[:15]

        # Fallback: POST to search page
        search_url = "https://www.superchef.pk/search"
        try:
            resp = _safe_request(
                search_url, proxy_manager, rotate_ua,
                method="post",
                data={"search_word": query},
            )
            if resp:
                soup = BeautifulSoup(resp.text, "html.parser")
                for card in soup.select(".recipe-card, .card, .recipe-item, .col-lg-4, .col-md-6"):
                    a = card.select_one("a")
                    if a:
                        title = ""
                        h = card.select_one("h3, h4, h5, h2")
                        if h:
                            title = h.get_text(strip=True)
                        elif a.get_text(strip=True):
                            title = a.get_text(strip=True)
                        href = a.get("href", "")
                        if title and href and len(title) > 3:
                            if not href.startswith("http"):
                                href = "https://www.superchef.pk" + href
                            results.append({
                                "title": title,
                                "source": "SuperChef",
                                "url": href,
                                "prep_time": "",
                            })
                if results:
                    return results[:15]
        except Exception:
            pass

        # Final fallback: use DuckDuckGo to find SuperChef results
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            ddg_results = DDGS().text(f"site:superchef.pk {query}", max_results=8)
            for r in ddg_results:
                title = r.get("title", "")
                # Clean up title: remove "by SuperChef", "| SooperChef" etc
                for sep in [" | ", " - ", " by ", " Recipe by"]:
                    if sep in title:
                        title = title.split(sep)[0]
                title = title.replace("Recipe", "").replace("recipe", "").strip()
                title = " ".join(title.split())  # normalize whitespace
                if len(title) < 4:
                    continue
                href = r.get("href", "")
                # Skip category/landing pages
                if href.rstrip("/").endswith(("-recipes", "/blog")):
                    continue
                results.append({
                    "title": title,
                    "source": "SuperChef",
                    "url": href,
                    "prep_time": "",
                })
        except Exception:
            pass
    except Exception:
        pass
    return results[:15]


# ---------------------------------------------------------------------------
# Scraper: Tasty
# ---------------------------------------------------------------------------

def search_tasty(query: str, proxy_manager=None, rotate_ua=True) -> list[dict]:
    results = []
    try:
        url = f"https://tasty.co/search?q={quote_plus(query)}"
        resp = _safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            return results
        soup = BeautifulSoup(resp.text, "html.parser")

        # Parse __NEXT_DATA__ JSON
        script = soup.select_one("script#__NEXT_DATA__")
        if script and script.string:
            data = json.loads(script.string)
            items = (
                data.get("props", {})
                .get("pageProps", {})
                .get("initialFeed", {})
                .get("items", [])
            )
            for item in items:
                if item.get("type") != "recipe":
                    continue
                name = item.get("name", "")
                slug = item.get("slug", "")
                link = f"https://tasty.co/recipe/{slug}" if slug else ""
                prep_time = ""
                times = item.get("times", {})
                if times.get("total_time", {}).get("display"):
                    prep_time = times["total_time"]["display"]
                if name and link:
                    results.append({
                        "title": name,
                        "source": "Tasty",
                        "url": link,
                        "prep_time": prep_time,
                    })
        # Fallback: parse HTML directly if __NEXT_DATA__ missing
        if not results:
            for a in soup.select("a[href*='/recipe/']"):
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if title and len(title) > 3 and href:
                    if not href.startswith("http"):
                        href = "https://tasty.co" + href
                    results.append({
                        "title": title,
                        "source": "Tasty",
                        "url": href,
                        "prep_time": "",
                    })
    except Exception:
        pass
    return results[:15]


# ---------------------------------------------------------------------------
# Scraper: DuckDuckGo Web Search
# ---------------------------------------------------------------------------

def search_web(query: str, proxy_manager=None, rotate_ua=True) -> list[dict]:
    results = []
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        search_query = f"{query} recipe"
        ddg_results = DDGS().text(search_query, max_results=15)
        for r in ddg_results:
            title = r.get("title", "")
            href = r.get("href", "")
            if title and href:
                source_name = ""
                try:
                    parsed = urlparse(href)
                    source_name = parsed.netloc.replace("www.", "")
                except Exception:
                    source_name = "Web"
                results.append({
                    "title": title,
                    "source": f"Web: {source_name}",
                    "url": href,
                    "prep_time": "",
                })
    except Exception:
        pass
    return results


# ---------------------------------------------------------------------------
# Override CustomTkinter icon behaviour
# ---------------------------------------------------------------------------

def _patch_ctk_icon():
    """Prevent CustomTkinter from overriding our taskbar/window icon."""
    try:
        if hasattr(ctk.CTk, "_windows_set_titlebar_icon"):
            def patched(self):
                try:
                    if ICON_PATH.exists():
                        self.iconbitmap(str(ICON_PATH))
                except Exception:
                    pass
            ctk.CTk._windows_set_titlebar_icon = patched
    except Exception:
        pass


# ---------------------------------------------------------------------------
# GUI Application
# ---------------------------------------------------------------------------

class CulinaryIndexApp(ctk.CTk):
    def __init__(self):
        _patch_ctk_icon()
        super().__init__()

        self.settings = load_settings()
        self.proxy_manager = ProxyManager(
            mode=self.settings.get("proxy_mode", "none"),
            custom_proxies=self.settings.get("custom_proxies", ""),
        )
        self._searching = False
        self._results: list[dict] = []
        self._result_widgets: list = []

        self.title(APP_NAME)
        self.geometry(self.settings.get("window_geometry", "960x720"))
        self.minsize(750, 550)

        # Set icon
        try:
            if ICON_PATH.exists():
                self.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        # Configure dark theme colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 0))
        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header, text=APP_NAME, font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#4a8fd4",
        )
        title_label.grid(row=0, column=0, sticky="w")

        # --- Search bar ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(8, 5))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search recipes... (e.g. chicken, biryani, pasta)",
            font=ctk.CTkFont(size=14),
            height=42,
            corner_radius=8,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._on_search())

        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            width=110,
            corner_radius=8,
            fg_color="#4a6fa5",
            hover_color="#5a8fc5",
            command=self._on_search,
        )
        self.search_btn.grid(row=0, column=1)

        # --- Tab view ---
        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)

        self.tab_primary = self.tabview.add("Primary Results")
        self.tab_web = self.tabview.add("Web Search")
        self.tab_settings = self.tabview.add("Settings")

        self._build_primary_tab()
        self._build_web_tab()
        self._build_settings_tab()

        # --- Status bar ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent", height=28)
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 8))
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_var = ctk.StringVar(value="Ready. Enter a recipe name to search.")
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        # Progress bar (hidden by default)
        self.progress = ctk.CTkProgressBar(self.status_frame, width=150, height=10)
        self.progress.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.progress.set(0)
        self.progress.grid_remove()

        # Focus search
        self.search_entry.focus()

    def _build_primary_tab(self):
        self.tab_primary.grid_columnconfigure(0, weight=1)
        self.tab_primary.grid_rowconfigure(1, weight=1)

        # Source indicators
        self.source_frame = ctk.CTkFrame(self.tab_primary, fg_color="transparent", height=30)
        self.source_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))

        self.source_indicators = {}
        for i, (key, name) in enumerate(
            [("foodfusion", "Food Fusion"), ("superchef", "SuperChef"), ("tasty", "Tasty")]
        ):
            dot = ctk.CTkLabel(
                self.source_frame, text=f"  {name}",
                font=ctk.CTkFont(size=11), text_color="#666666",
            )
            dot.grid(row=0, column=i, padx=8, sticky="w")
            self.source_indicators[key] = dot

        # Scrollable results area
        self.primary_scroll = ctk.CTkScrollableFrame(
            self.tab_primary, corner_radius=0, fg_color="transparent",
        )
        self.primary_scroll.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.primary_scroll.grid_columnconfigure(0, weight=1)

    def _build_web_tab(self):
        self.tab_web.grid_columnconfigure(0, weight=1)
        self.tab_web.grid_rowconfigure(0, weight=1)

        self.web_scroll = ctk.CTkScrollableFrame(
            self.tab_web, corner_radius=0, fg_color="transparent",
        )
        self.web_scroll.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.web_scroll.grid_columnconfigure(0, weight=1)

    def _build_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)

        row = 0

        # Sources section
        sources_label = ctk.CTkLabel(
            self.tab_settings, text="Recipe Sources",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        sources_label.grid(row=row, column=0, sticky="w", padx=20, pady=(15, 5))
        row += 1

        self.source_vars = {}
        for key, name in [
            ("foodfusion", "Food Fusion (foodfusion.com)"),
            ("superchef", "SuperChef (superchef.pk)"),
            ("tasty", "Tasty (tasty.co)"),
            ("web", "Web Search (DuckDuckGo)"),
        ]:
            var = ctk.BooleanVar(value=self.settings["sources"].get(key, True))
            cb = ctk.CTkCheckBox(
                self.tab_settings, text=name, variable=var,
                font=ctk.CTkFont(size=13), checkbox_width=22, checkbox_height=22,
            )
            cb.grid(row=row, column=0, sticky="w", padx=30, pady=3)
            self.source_vars[key] = var
            row += 1

        # Separator
        sep1 = ctk.CTkFrame(self.tab_settings, height=1, fg_color="#333333")
        sep1.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        row += 1

        # Proxy section
        proxy_label = ctk.CTkLabel(
            self.tab_settings, text="Proxy Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        proxy_label.grid(row=row, column=0, sticky="w", padx=20, pady=(5, 5))
        row += 1

        self.proxy_mode_var = ctk.StringVar(value=self.settings.get("proxy_mode", "none"))
        for mode, label in [
            ("none", "None (direct requests) - Recommended"),
            ("free", "Free rotating proxies (auto-fetched)"),
            ("custom", "Custom proxy list"),
        ]:
            rb = ctk.CTkRadioButton(
                self.tab_settings, text=label, variable=self.proxy_mode_var, value=mode,
                font=ctk.CTkFont(size=13),
            )
            rb.grid(row=row, column=0, sticky="w", padx=30, pady=3)
            row += 1

        # Custom proxy text box
        self.custom_proxy_text = ctk.CTkTextbox(
            self.tab_settings, height=80, font=ctk.CTkFont(size=12, family="Consolas"),
            corner_radius=6,
        )
        self.custom_proxy_text.grid(row=row, column=0, sticky="ew", padx=30, pady=5)
        self.custom_proxy_text.insert(
            "0.0", self.settings.get("custom_proxies", "http://ip:port\nhttp://ip:port")
        )
        row += 1

        self.proxy_status_var = ctk.StringVar(value="Proxy status: not tested")
        proxy_status = ctk.CTkLabel(
            self.tab_settings, textvariable=self.proxy_status_var,
            font=ctk.CTkFont(size=12), text_color="#888888",
        )
        proxy_status.grid(row=row, column=0, sticky="w", padx=30, pady=(0, 5))
        row += 1

        refresh_btn = ctk.CTkButton(
            self.tab_settings, text="Refresh Proxies", width=150, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#4a6fa5", hover_color="#5a8fc5",
            command=self._on_refresh_proxies,
        )
        refresh_btn.grid(row=row, column=0, sticky="w", padx=30, pady=(0, 10))
        row += 1

        # Separator
        sep2 = ctk.CTkFrame(self.tab_settings, height=1, fg_color="#333333")
        sep2.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        row += 1

        # Anti-block section
        anti_label = ctk.CTkLabel(
            self.tab_settings, text="Anti-Block Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        anti_label.grid(row=row, column=0, sticky="w", padx=20, pady=(5, 5))
        row += 1

        self.rotate_ua_var = ctk.BooleanVar(value=self.settings.get("rotate_ua", True))
        ua_cb = ctk.CTkCheckBox(
            self.tab_settings,
            text="Rotate browser User-Agent headers (anti-detection)",
            variable=self.rotate_ua_var,
            font=ctk.CTkFont(size=13), checkbox_width=22, checkbox_height=22,
        )
        ua_cb.grid(row=row, column=0, sticky="w", padx=30, pady=3)
        row += 1

        # Separator
        sep3 = ctk.CTkFrame(self.tab_settings, height=1, fg_color="#333333")
        sep3.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        row += 1

        # Action buttons
        btn_frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="w", padx=20, pady=5)

        save_btn = ctk.CTkButton(
            btn_frame, text="Save Settings", width=140, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4a6fa5", hover_color="#5a8fc5",
            command=self._on_save_settings,
        )
        save_btn.grid(row=0, column=0, padx=(0, 10))

        clear_btn = ctk.CTkButton(
            btn_frame, text="Clear All Results", width=140, height=36,
            font=ctk.CTkFont(size=13),
            fg_color="#666666", hover_color="#888888",
            command=self._on_clear_results,
        )
        clear_btn.grid(row=0, column=1)

    # -----------------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------------

    def _on_search(self):
        if self._searching:
            return
        query = self.search_var.get().strip()
        if not query:
            self._show_warning("Please enter a search term.")
            return

        enabled = [k for k, v in self.source_vars.items() if v.get()]
        if not enabled:
            self._show_warning("Please enable at least one source in Settings.")
            return

        self._searching = True
        self.search_btn.configure(state="disabled", text="Searching...")
        self._clear_results_ui()
        self._results.clear()

        # Reset source indicators
        for key, dot in self.source_indicators.items():
            dot.configure(text_color="#666666")

        # Show progress
        self.progress.grid()
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        self.status_var.set(f'Searching for "{query}"...')

        # Prepare proxy manager
        pm = None
        mode = self.proxy_mode_var.get()
        if mode == "free":
            pm = self.proxy_manager
            pm._mode = "free"
        elif mode == "custom":
            custom = self.custom_proxy_text.get("0.0", "end").strip()
            pm = ProxyManager(mode="custom", custom_proxies=custom)
        else:
            pm = ProxyManager(mode="none")

        rotate_ua = self.rotate_ua_var.get()

        # Build scraper map for enabled sources
        scrapers = {}
        if self.source_vars["foodfusion"].get():
            scrapers["Food Fusion"] = ("foodfusion", search_foodfusion)
        if self.source_vars["superchef"].get():
            scrapers["SuperChef"] = ("superchef", search_superchef)
        if self.source_vars["tasty"].get():
            scrapers["Tasty"] = ("tasty", search_tasty)
        if self.source_vars["web"].get():
            scrapers["Web"] = ("web", search_web)

        if not scrapers:
            self._searching = False
            self.search_btn.configure(state="normal", text="Search")
            self.progress.stop()
            self.progress.grid_remove()
            return

        completed_count = [0]
        total = len(scrapers)

        def run_scraper(source_name, source_key, scraper_fn):
            try:
                results = scraper_fn(query, proxy_manager=pm, rotate_ua=rotate_ua)
            except Exception:
                results = []
            self.after(0, lambda: self._on_source_complete(
                source_name, source_key, results, completed_count, total, query,
            ))

        for source_name, (source_key, scraper_fn) in scrapers.items():
            t = threading.Thread(
                target=run_scraper, args=(source_name, source_key, scraper_fn),
                daemon=True,
            )
            t.start()

    def _on_source_complete(self, source_name, source_key, results, completed_count, total, query):
        completed_count[0] += 1

        # Update source indicator
        if source_key in self.source_indicators:
            dot = self.source_indicators[source_key]
            if results:
                dot.configure(text_color="#4CAF50")
            else:
                dot.configure(text_color="#F44336")

        # Add results to UI
        if source_key == "web":
            target_tab = self.web_scroll
        else:
            target_tab = self.primary_scroll

        for r in results:
            self._results.append(r)
            self._add_result_card(target_tab, r)

        # Update status
        self.status_var.set(
            f"Searching... {completed_count[0]}/{total} sources done. "
            f"{len(self._results)} results found."
        )

        # All done?
        if completed_count[0] >= total:
            self._searching = False
            self.search_btn.configure(state="normal", text="Search")
            self.progress.stop()
            self.progress.grid_remove()
            if self._results:
                self.status_var.set(
                    f'Search complete. {len(self._results)} results for "{query}".'
                )
            else:
                self.status_var.set(
                    f'No recipes found for "{query}". Try a different search term.'
                )

    def _add_result_card(self, parent, result: dict):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color="#2b2b3d", border_width=1, border_color="#3a3a4d")
        card.grid(sticky="ew", padx=5, pady=4)
        card.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            card, text=result["title"], font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w", wraplength=500,
        )
        title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        # Source + prep time
        info_text = f"Source: {result['source']}"
        if result.get("prep_time"):
            info_text += f"    Prep: {result['prep_time']}"
        info_label = ctk.CTkLabel(
            card, text=info_text, font=ctk.CTkFont(size=11),
            text_color="#888888", anchor="w",
        )
        info_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 2))

        # URL preview
        url_text = result["url"]
        if len(url_text) > 65:
            url_text = url_text[:62] + "..."
        url_label = ctk.CTkLabel(
            card, text=url_text, font=ctk.CTkFont(size=10),
            text_color="#5a6a7a", anchor="w",
        )
        url_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))

        # Open button
        open_btn = ctk.CTkButton(
            card, text="Open Recipe", width=110, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#4a6fa5", hover_color="#5a8fc5", corner_radius=6,
            command=lambda u=result["url"]: webbrowser.open(u),
        )
        open_btn.grid(row=0, column=1, rowspan=3, padx=12, pady=10, sticky="e")

        self._result_widgets.append(card)

    def _clear_results_ui(self):
        for w in self._result_widgets:
            w.destroy()
        self._result_widgets.clear()

    def _on_clear_results(self):
        self._clear_results_ui()
        self._results.clear()
        for key, dot in self.source_indicators.items():
            dot.configure(text_color="#666666")
        self.status_var.set("Results cleared.")

    def _on_refresh_proxies(self):
        self.proxy_status_var.set("Fetching proxies... (this may take 15-30 seconds)")

        def do_refresh():
            count = self.proxy_manager.fetch_free_proxies(
                status_callback=lambda msg: self.after(0, lambda: self.proxy_status_var.set(msg))
            )
            self.after(0, lambda: self.proxy_status_var.set(
                f"Proxy status: {count} working proxies ready"
            ))

        threading.Thread(target=do_refresh, daemon=True).start()

    def _on_save_settings(self):
        self.settings["sources"] = {k: v.get() for k, v in self.source_vars.items()}
        self.settings["proxy_mode"] = self.proxy_mode_var.get()
        self.settings["custom_proxies"] = self.custom_proxy_text.get("0.0", "end").strip()
        self.settings["rotate_ua"] = self.rotate_ua_var.get()
        self.settings["window_geometry"] = self.geometry()
        save_settings(self.settings)

        self.proxy_manager = ProxyManager(
            mode=self.settings["proxy_mode"],
            custom_proxies=self.settings["custom_proxies"],
        )

        self.status_var.set("Settings saved.")

    def _show_warning(self, msg: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Warning")
        dialog.geometry("320x140")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        try:
            if ICON_PATH.exists():
                dialog.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        label = ctk.CTkLabel(
            dialog, text=msg, font=ctk.CTkFont(size=13), wraplength=280,
        )
        label.pack(pady=(25, 15), padx=20)

        ok_btn = ctk.CTkButton(
            dialog, text="OK", width=80, height=32,
            command=dialog.destroy,
        )
        ok_btn.pack(pady=(0, 15))

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 160
        y = self.winfo_y() + (self.winfo_height() // 2) - 70
        dialog.geometry(f"+{x}+{y}")

    # -----------------------------------------------------------------------
    # Window lifecycle
    # -----------------------------------------------------------------------

    def destroy(self):
        self.settings["window_geometry"] = self.geometry()
        save_settings(self.settings)
        super().destroy()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = CulinaryIndexApp()
    app.mainloop()


if __name__ == "__main__":
    main()
