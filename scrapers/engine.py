from concurrent.futures import ThreadPoolExecutor, as_completed

from .foodfusion import search_foodfusion
from .superchef import search_superchef
from .tasty import search_tasty
from .duckduckgo import search_web

SCRAPERS = {
    "Food Fusion": search_foodfusion,
    "SuperChef": search_superchef,
    "Tasty": search_tasty,
    "Web": search_web,
}

# Reusable thread pool
executor = ThreadPoolExecutor(max_workers=4)


def run_all_scrapers(query, timeout=25):
    """Run all scrapers concurrently. Returns combined results list with source labels."""
    all_results = []
    futures = {
        executor.submit(fn, query): name
        for name, fn in SCRAPERS.items()
    }
    for future in as_completed(futures, timeout=timeout):
        source_name = futures[future]
        try:
            results = future.result(timeout=5)
            all_results.extend(results)
        except Exception:
            pass
    return all_results
