"""Stackit unified runner script to launch FastAPI backend and Streamlit frontend."""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_dependencies():
    """Ensures processed data is generated before launching servers."""
    processed_file = BASE_DIR / "data" / "processed" / "stock_statistics.csv"
    if not processed_file.exists():
        print("[Stackit] Processed data not found. Running preprocessing pipeline...")
        cmd = [sys.executable, str(BASE_DIR / "scripts" / "preprocess_data.py")]
        subprocess.run(cmd, check=True)

def main():
    print("\n" + "=" * 60)
    print("                STACKIT: SYSTEM LAUNCHER")
    print("=" * 60 + "\n")

    check_dependencies()

    backend_port = 8000
    frontend_port = 8501

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)

    # 1. Start FastAPI backend with uvicorn
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.backend.main:app",
        "--host", "127.0.0.1",
        "--port", str(backend_port)
    ]

    print(f"[Stackit] Starting FastAPI backend on http://127.0.0.1:{backend_port}...")
    backend_process = subprocess.Popen(backend_cmd, env=env)

    # Brief delay to allow FastAPI to bind port
    time.sleep(2.0)

    # 2. Start Streamlit frontend
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(BASE_DIR / "app" / "frontend" / "main.py"),
        "--server.port", str(frontend_port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]

    print(f"[Stackit] Starting Streamlit frontend on http://localhost:{frontend_port}...")
    frontend_process = subprocess.Popen(frontend_cmd, env=env)

    print("\n" + "-" * 60)
    print(f"✅ Stackit is running successfully!")
    print(f"👉 Frontend Dashboard: http://localhost:{frontend_port}")
    print(f"👉 Backend API Docs:   http://127.0.0.1:{backend_port}/docs")
    print("-" * 60)
    print("Press Ctrl+C to terminate both servers.\n")

    def shutdown(sig, frame):
        print("\n[Stackit] Shutting down servers...")
        try:
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait(timeout=3)
            frontend_process.wait(timeout=3)
        except Exception:
            backend_process.kill()
            frontend_process.kill()
        print("[Stackit] Servers stopped cleanly. Goodbye.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
            # If any process terminated prematurely, exit
            if backend_process.poll() is not None:
                print("[Stackit] Backend process terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("[Stackit] Frontend process terminated unexpectedly.")
                break
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
