"""
Unified Runner for AI Music Source Separation
Supports starting both Frontend (port 3000) and Backend (port 5000) simultaneously,
or running either service individually.
"""
import os
import sys
import time
import signal
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BANNER = """
=======================================================================
           AI MUSIC SOURCE SEPARATION - DUAL SERVER SYSTEM
=======================================================================
   [Frontend UI]  : http://localhost:{front_port} (Flask + Bootstrap 5)
   [Backend API]  : http://localhost:{back_port} (REST API & Separator)
   [Docs/Health]  : http://localhost:{back_port}/api/health
=======================================================================
   Press Ctrl + C to stop all servers.
=======================================================================
"""

def run_backend(port=5000):
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["NUMBA_CACHE_DIR"] = str(BASE_DIR / "data" / "numba_cache")
    backend_script = str(BASE_DIR / "backend.py")
    print(f"[*] Launching Backend API on http://localhost:{port}...")
    return subprocess.Popen([sys.executable, backend_script], env=env, cwd=str(BASE_DIR))

def run_frontend(port=3000, backend_url="http://localhost:5000"):
    env = os.environ.copy()
    env["FRONTEND_PORT"] = str(port)
    env["PORT"] = str(port)
    env["BACKEND_URL"] = backend_url
    env["NUMBA_CACHE_DIR"] = str(BASE_DIR / "data" / "numba_cache")
    frontend_script = str(BASE_DIR / "frontend.py")
    print(f"[*] Launching Frontend UI on http://localhost:{port} (Targeting Backend: {backend_url})...")
    return subprocess.Popen([sys.executable, frontend_script], env=env, cwd=str(BASE_DIR))

def main():
    parser = argparse.ArgumentParser(description="AI Music Separation Launcher")
    parser.add_argument("--backend", "-b", action="store_true", help="Chỉ chạy Backend API (Port 5000)")
    parser.add_argument("--frontend", "-f", action="store_true", help="Chỉ chạy Frontend UI (Port 3000)")
    parser.add_argument("--port-front", type=int, default=3000, help="Cổng cho Frontend (Mặc định: 3000)")
    parser.add_argument("--port-back", type=int, default=5000, help="Cổng cho Backend (Mặc định: 5000)")
    args = parser.parse_args()

    procs = []

    def cleanup(signum=None, frame=None):
        print("\n[!] Shutting down all services...")
        for p in procs:
            if p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=3)
                except Exception:
                    p.kill()
        print("[+] All services stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    front_port = args.port_front
    back_port = args.port_back
    backend_url = f"http://localhost:{back_port}"

    if args.backend and not args.frontend:
        # Chạy chỉ backend
        print(f"[*] Starting ONLY Backend API on port {back_port}...")
        p = run_backend(port=back_port)
        procs.append(p)
    elif args.frontend and not args.backend:
        # Chạy chỉ frontend
        print(f"[*] Starting ONLY Frontend UI on port {front_port}...")
        p = run_frontend(port=front_port, backend_url=backend_url)
        procs.append(p)
    else:
        # Chạy cả hai dịch vụ
        print(BANNER.format(front_port=front_port, back_port=back_port))
        p_back = run_backend(port=back_port)
        procs.append(p_back)
        time.sleep(1)  # Đợi backend khởi động
        p_front = run_frontend(port=front_port, backend_url=backend_url)
        procs.append(p_front)

    try:
        # Giữ tiến trình sống và giám sát các tiến trình con
        while True:
            for p in procs:
                if p.poll() is not None:
                    print(f"[!] Warning: Process {p.pid} exited with code {p.returncode}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
