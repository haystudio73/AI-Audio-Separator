"""
AI Music Source Separation - Entry Point & Backward Compatibility Wrapper
Exports the Flask app from backend.py.
"""
import os
from backend import app, logger

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting AI Music Separation Backend Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
