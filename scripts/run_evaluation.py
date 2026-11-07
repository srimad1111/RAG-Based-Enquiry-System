"""
Script to execute the Phase 7 Comprehensive RAG Evaluation Benchmark.
Usage:
    python scripts/run_evaluation.py
    or
    python -m app.evaluation.run_evaluation
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.evaluation.run_evaluation import run_evaluation_cli

if __name__ == "__main__":
    run_evaluation_cli()
