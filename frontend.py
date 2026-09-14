import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, Response, jsonify
import requests

from config import BASE_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [FRONTEND] - %(levelname)s - %(message)s")
logger = logging.getLogger("frontend")

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static"
)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

# Backend URL configuration (Port 5000)
DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

@app.route("/")
def index():
    """Phục vụ giao diện Bootstrap 5 người dùng và truyền backend API URL"""
    backend_url = os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL)
    return render_template("index.html", backend_url=backend_url)

@app.route("/health")
def frontend_health():
    """Kiểm tra trạng thái máy chủ frontend"""
    backend_url = os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL)
    return jsonify({
        "status": "online",
        "service": "AI Music Source Separation Frontend UI",
        "port": int(os.environ.get("FRONTEND_PORT", os.environ.get("PORT", 3000))),
        "configured_backend_url": backend_url
    })

# Reverse-proxy fallback: Trong trường hợp client gặp vấn đề CORS hoặc truy cập qua mạng nội bộ,
# Frontend có thể chuyển tiếp yêu cầu /api/<endpoint> đến Backend (port 5000) một cách liền mạch.
@app.route("/api/<path:endpoint>", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
def proxy_to_backend(endpoint):
    backend_url = os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL)
    target_url = f"{backend_url}/api/{endpoint}"
    
    headers = {key: value for (key, value) in request.headers if key.lower() not in ["host", "content-length"]}
    
    try:
        if request.files:
            files = {name: (file.filename, file.stream, file.content_type) for name, file in request.files.items()}
            data = request.form.to_dict()
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=data,
                files=files,
                params=request.args,
                timeout=600
            )
        else:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                params=request.args,
                timeout=600
            )
        
        # Bỏ hop-by-hop headers
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        response_headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(resp.content, resp.status_code, response_headers)
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy request to {target_url} failed: {e}")
        return jsonify({
            "success": False,
            "error": f"Không thể kết nối tới Backend API (port 5000): {str(e)}",
            "error_en": f"Failed to connect to Backend API (port 5000): {str(e)}"
        }), 502

if __name__ == "__main__":
    port = int(os.environ.get("FRONTEND_PORT", os.environ.get("PORT", 3000)))
    logger.info(f"Starting AI Music Separation Frontend UI on port {port}...")
    logger.info(f"Target Backend API: {DEFAULT_BACKEND_URL}")
    app.run(host="0.0.0.0", port=port, debug=False)
