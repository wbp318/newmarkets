"""
NewMarkets — Double-click to run.
Opens your browser automatically. Close this window to stop the server.
"""

import os
import sys
import threading
import time
import webbrowser

# When running as a PyInstaller bundle, files are in _MEIPASS
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set env so SQLite db lives next to the .exe (not inside the temp bundle)
if getattr(sys, "frozen", False):
    exe_dir = os.path.dirname(sys.executable)
    db_path = os.path.join(exe_dir, "newmarkets.db").replace("\\", "/")
    os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

    # Look for .env next to the exe
    env_file = os.path.join(exe_dir, ".env")
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)


def open_browser():
    """Wait for the server to start, then open the browser."""
    time.sleep(2)
    webbrowser.open("http://localhost:8000")


def main():
    print()
    print("=" * 50)
    print("  NewMarkets")
    print("  Cross-Market E-Commerce Arbitrage Toolkit")
    print("=" * 50)
    print()
    print("  Starting server...")
    print("  Your browser will open automatically.")
    print()
    print("  To stop: just close this window.")
    print("=" * 50)
    print()

    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start the server
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
