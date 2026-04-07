import logging
import os
import time
from flask import Flask, render_template, request, jsonify
from scrapers.engine import run_all_scrapers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
logger = logging.getLogger("app")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "culinary-index-secret")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("index.html")

    source_filter = request.args.get("source", "all")
    start = time.time()

    try:
        results = run_all_scrapers(query, timeout=25)
    except Exception as e:
        logger.error(f"Search failed for '{query}': {e}")
        results = []

    elapsed = round(time.time() - start, 1)
    logger.info(f"Search '{query}': {len(results)} results in {elapsed}s")

    if source_filter == "primary":
        results = [r for r in results if "Web:" not in r["source"]]
    elif source_filter == "web":
        results = [r for r in results if "Web:" in r["source"]]

    primary = [r for r in results if "Web:" not in r["source"]]
    web = [r for r in results if "Web:" in r["source"]]

    return render_template(
        "results.html",
        query=query,
        primary_results=primary,
        web_results=web,
        total_count=len(primary) + len(web),
        elapsed=elapsed,
        source_filter=source_filter,
    )


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter required"}), 400
    try:
        results = run_all_scrapers(query, timeout=25)
    except Exception as e:
        logger.error(f"API search failed for '{query}': {e}")
        results = []
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")


@app.route("/sw.js")
def sw():
    return app.send_static_file("service-worker.js")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
