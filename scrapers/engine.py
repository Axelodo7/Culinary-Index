import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .foodfusion import search_foodfusion
from .superchef import search_superchef
from .tasty import search_tasty
from .duckduckgo import search_web

logger = logging.getLogger("scrapers")

SCRAPERS = {
    "Food Fusion": search_foodfusion,
    "SuperChef": search_superchef,
    "Tasty": search_tasty,
    "Web": search_web,
}

executor = ThreadPoolExecutor(max_workers=4)


def run_all_scrapers(query, timeout=25):
    """Run all scrapers concurrently. Returns combined results list."""
    all_results = []
    futures = {
        executor.submit(fn, query): name
        for name, fn in SCRAPERS.items()
    }
    for future in as_completed(futures, timeout=timeout):
        source_name = futures[future]
        try:
            results = future.result(timeout=10)
            logger.info(f"{source_name}: {len(results)} results for '{query}'")
            all_results.extend(results)
        except Exception as e:
            logger.error(f"{source_name}: failed for '{query}': {type(e).__name__}: {e}")
    return all_results
