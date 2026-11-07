"""
Batch script to ingest all NexaDesk documentation files (PDF, DOCX, TXT, MD)
across v1.0, v2.0, and v3.0 into SQLite with clean chunking and metadata.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.core.config import get_settings
from app.services.ingestion_service import ingestion_service

settings = get_settings()
DOCS_DIR = settings.documents_path

CATEGORY_MAP = {
    "getting_started.md": "Getting Started",
    "ticket_management.md": "Ticket Lifecycle",
    "pricing_and_plans.md": "Pricing & Billing",
    "pricing_and_quotas.txt": "Pricing & Quotas",
    "email_and_sla_policy.pdf": "SLA & Protocols",
    "omnichannel_and_webhooks.pdf": "Omnichannel & Webhooks",
    "enterprise_ai_and_sso.pdf": "AI & Enterprise Security",
    "user_roles_guide.docx": "Access Control & Roles",
    "rbac_and_round_robin.docx": "RBAC & Routing",
    "nexaflow_studio_guide.docx": "Visual Workflows",
    "automations_and_routing.md": "Automation Rules",
    "ai_copilot_features.md": "AI Copilot",
}


def batch_ingest():
    print("=" * 65)
    print("NexaDesk Documentation Batch Ingestion Pipeline (Phase 2)")
    print("=" * 65)

    total_ingested = 0
    total_chunks = 0

    for version in settings.SUPPORTED_PRODUCT_VERSIONS:
        version_dir = DOCS_DIR / version
        if not version_dir.exists():
            continue

        print(f"\nProcessing version: [{version}] from {version_dir.name}...")
        files = [f for f in version_dir.iterdir() if f.is_file() and not f.name.startswith(".")]

        for file_path in sorted(files):
            category = CATEGORY_MAP.get(file_path.name, "General Documentation")
            try:
                res = ingestion_service.ingest_file(
                    file_bytes=file_path.read_bytes(),
                    filename=file_path.name,
                    product_name="NexaDesk",
                    product_version=version,
                    category=category,
                    chunk_size=800,
                    chunk_overlap=150,
                    replace_existing=True
                )
                print(f"  [OK] {file_path.name} ({file_path.suffix.upper()}) -> {res.chunks_created} chunks | Doc ID: {res.document.id}")
                total_ingested += 1
                total_chunks += res.chunks_created
            except Exception as e:
                print(f"  [FAIL] {file_path.name}: {e}")

    print("\n" + "=" * 65)
    print(f"Batch Ingestion Complete: Ingested {total_ingested} documents into {total_chunks} structured chunks.")
    print("=" * 65)


if __name__ == "__main__":
    batch_ingest()

