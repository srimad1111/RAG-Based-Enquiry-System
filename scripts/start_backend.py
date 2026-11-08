import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.core.config import get_settings
from app.main import app

if __name__ == "__main__":
    settings = get_settings()
    print(f"Starting NexaDesk Backend on {settings.HOST}:{settings.PORT}...", flush=True)
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
