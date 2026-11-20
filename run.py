"""
Entry point to run the BBQ Online Store unified application.
Run: python run.py
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    print("=" * 60)
    print(f"🔥 BBQ HOUSE - ONLINE STORE RUNNING AT:")
    print(f"   Local URL:    http://127.0.0.1:{port}")
    print(f"   Network URL:  http://localhost:{port}")
    print(f"   API Docs:     http://localhost:{port}/docs")
    print("=" * 60)
    uvicorn.run("main:app", host=host, port=port, reload=False)
