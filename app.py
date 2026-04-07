import logging
import os
import time
from flask import Flask, render_template, render_template_string, request, jsonify
from scrapers.engine import run_all_scrapers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
logger = logging.getLogger("app")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "culinary-index-secret")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # 1 year for static files


@app.after_request
def add_cache_headers(response):
    # Only service-worker itself should never be cached
    if request.path == '/sw.js':
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


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
    resp = app.send_static_file("service-worker.js")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/download")
def download():
    from flask import send_from_directory
    import os
    apk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile", "android", "app", "build", "outputs", "apk", "debug")
    if os.path.exists(os.path.join(apk_path, "app-debug.apk")):
        return send_from_directory(apk_path, "app-debug.apk", as_attachment=True, download_name="CulinaryIndex.apk")
    return render_template_string(
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link rel='stylesheet' href='/static/css/style.css?v=3'></head><body>"
        "<div style='max-width:500px;margin:3rem auto;padding:2rem;text-align:center;font-family:Inter,system-ui,sans-serif;'>"
        "<h1 style='color:var(--accent);'>App Not Ready Yet</h1>"
        "<p style='color:var(--text-secondary);margin-top:1rem;'>The APK hasn't been built yet. "
        "Run these commands on your PC:</p>"
        "<pre style='background:var(--bg-card);padding:1rem;border-radius:8px;text-align:left;margin:1rem 0;font-size:0.85rem;overflow-x:auto;'>"
        "cd C:\\Users\\Ayyan\\CulinaryIndex\\mobile\n"
        "npx cap sync android\n"
        ".\\android\\gradlew.bat assembleDebug</pre>"
        "<p style='color:var(--text-secondary);font-size:0.85rem;'>Then place the APK at <code>mobile/android/app/build/outputs/apk/debug/app-debug.apk</code></p>"
        "<a href='/' style='display:inline-block;margin-top:1.5rem;color:var(--accent);text-decoration:none;font-weight:600;'>&larr; Back to search</a>"
        "</div></body></html>"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
