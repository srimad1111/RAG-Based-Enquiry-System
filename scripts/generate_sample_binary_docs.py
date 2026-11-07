"""
Script to generate actual binary sample documents (PDF, DOCX, TXT, MD)
across NexaDesk v1.0, v2.0, and v3.0 with distinct feature behaviors,
including versioned report export capabilities.
"""

from pathlib import Path
import docx
import pymupdf as fitz

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "backend" / "data" / "documents" / "NexaDesk"


def create_pdf(file_path: Path, title: str, sections: list):
    """Generate an actual PDF file with PyMuPDF with structured pages and headings."""
    doc = fitz.open()
    for sec_title, sec_text in sections:
        page = doc.new_page(width=595, height=842)  # A4 size
        page.insert_text(fitz.Point(50, 60), title, fontsize=11, color=(0.4, 0.4, 0.4))
        page.insert_text(fitz.Point(50, 100), sec_title, fontsize=16, color=(0.1, 0.1, 0.6))
        rect = fitz.Rect(50, 130, 545, 780)
        page.insert_textbox(rect, sec_text, fontsize=10, lineheight=1.3)
    doc.save(str(file_path))
    doc.close()
    print(f"  [+] Created PDF: {file_path.name}")


def create_docx(file_path: Path, title: str, sections: list):
    """Generate an actual DOCX file with python-docx with headings and tables."""
    doc = docx.Document()
    doc.add_heading(title, level=0)
    for sec_title, sec_text in sections:
        doc.add_heading(sec_title, level=1)
        doc.add_paragraph(sec_text)
    doc.save(str(file_path))
    print(f"  [+] Created DOCX: {file_path.name}")


def create_txt(file_path: Path, title: str, sections: list):
    """Generate a clean TXT file with section headers."""
    content = f"=== {title} ===\n\n"
    for sec_title, sec_text in sections:
        content += f"[{sec_title}]\n{sec_text}\n\n"
    file_path.write_text(content.strip(), encoding="utf-8")
    print(f"  [+] Created TXT: {file_path.name}")


def create_md(file_path: Path, title: str, sections: list):
    """Generate a clean Markdown file with section headers."""
    content = f"# {title}\n\n"
    for sec_title, sec_text in sections:
        content += f"## {sec_title}\n\n{sec_text}\n\n"
    file_path.write_text(content.strip(), encoding="utf-8")
    print(f"  [+] Created MD: {file_path.name}")


def generate_all():
    print("Generating real documentation files for NexaDesk across v1.0, v2.0, and v3.0...")

    # ==========================================
    # Version 1.0 Docs
    # ==========================================
    v1_dir = DOCS_DIR / "v1.0"
    v1_dir.mkdir(parents=True, exist_ok=True)

    create_pdf(
        v1_dir / "email_and_sla_policy.pdf",
        "NexaDesk v1.0 - Technical Documentation",
        [
            (
                "POP3 Email Polling Configuration",
                "In NexaDesk v1.0, email ingestion is handled strictly via scheduled POP3/IMAP polling.\n\n"
                "System administrators must provide the mail server host, port 995 for SSL POP3, or port 993 for IMAP.\n"
                "The email polling worker runs once every 10 minutes. Real-time push webhooks are NOT supported in v1.0.\n"
                "Attachment Limitation: Incoming emails with attachments exceeding 5 MB will be rejected."
            ),
            (
                "SLA Policy and Resolution Deadlines",
                "NexaDesk v1.0 defines fixed, non-customizable SLA resolution targets:\n\n"
                "1. Urgent Severity: 4 hours total resolution deadline.\n"
                "2. Medium Severity: 12 hours total resolution deadline.\n"
                "3. Low Severity: 24 hours total resolution deadline.\n\n"
                "SLA clocks run 24/7 without business-hour exclusions."
            )
        ]
    )

    create_docx(
        v1_dir / "user_roles_guide.docx",
        "NexaDesk v1.0 Role-Based Access Control",
        [
            (
                "Standard Roles in v1.0",
                "NexaDesk v1.0 supports exactly two user roles: Administrator and Agent.\n\n"
                "- Administrator: Full system access, email mailbox settings, user provisioning.\n"
                "- Agent: Can view assigned tickets, post public replies, and mark tickets as closed.\n\n"
                "Granular permissions or custom roles are not supported in version 1.0."
            )
        ]
    )

    create_txt(
        v1_dir / "pricing_and_quotas.txt",
        "NexaDesk v1.0 Pricing Tiers",
        [
            (
                "Monthly Subscription Tiers",
                "Free Community: Free for up to 2 agents, 100 tickets per month.\n"
                "Starter Tier: $19 per agent per month, unlimited tickets, email support.\n"
                "Pro Tier: $49 per agent per month, custom domain, priority queue.\n\n"
                "Billing Policy: All billing is month-to-month. Annual discounts are NOT available in v1.0."
            )
        ]
    )

    create_md(
        v1_dir / "reporting_and_exports.md",
        "NexaDesk v1.0 Reporting and Analytics",
        [
            (
                "Manual Report Exports in v1.0",
                "NexaDesk v1.0 supports manual report exports only.\n\n"
                "Administrators must manually click the 'Export CSV' button on the ticket ledger page to download ticket history.\n"
                "Supported format: Raw CSV format only.\n"
                "Scheduled report delivery, recurring email reports, and automated background exports are NOT supported in v1.0."
            )
        ]
    )

    # ==========================================
    # Version 2.0 Docs
    # ==========================================
    v2_dir = DOCS_DIR / "v2.0"
    v2_dir.mkdir(parents=True, exist_ok=True)

    create_pdf(
        v2_dir / "omnichannel_and_webhooks.pdf",
        "NexaDesk v2.0 - Technical Documentation",
        [
            (
                "Deprecation of POP3 and Real-Time Webhooks",
                "The legacy POP3 polling worker from v1.0 is officially DEPRECATED.\n"
                "Incoming emails must now be routed via SendGrid Inbound Parse or Mailgun HTTP Webhooks.\n"
                "Maximum attachment size has been increased to 25 MB."
            ),
            (
                "Live Chat Widget and Slack Integration",
                "NexaDesk v2.0 introduces omnichannel communication:\n"
                "- Web Live Chat Widget for customer websites.\n"
                "- Slack Support App allowing agents to respond to customer inquiries from Slack."
            )
        ]
    )

    create_docx(
        v2_dir / "rbac_and_round_robin.docx",
        "NexaDesk v2.0 Advanced Routing & Roles",
        [
            (
                "Enhanced RBAC Roles",
                "NexaDesk v2.0 expands user roles to four tiers: Admin, Manager, Agent, and Read-Only Viewer."
            ),
            (
                "Automated Round-Robin Routing",
                "In v2.0, manual ticket assignment is replaced by automated round-robin dispatch based on agent capacity."
            )
        ]
    )

    create_txt(
        v2_dir / "pricing_and_quotas.txt",
        "NexaDesk v2.0 Pricing Tiers",
        [
            (
                "Revised Subscription Plans",
                "Starter Tier: $29 per agent per month, includes Live Chat widget.\n"
                "Growth Tier: $79 per agent per month, includes Round-Robin routing and Slack integration.\n"
                "Enterprise Tier: $149 per agent per month, custom SLA schedules.\n\n"
                "Annual Discount: 15% discount applies when paying annually upfront."
            )
        ]
    )

    create_md(
        v2_dir / "reporting_and_exports.md",
        "NexaDesk v2.0 Reporting and Analytics",
        [
            (
                "Scheduled Report Exports in v2.0",
                "NexaDesk v2.0 introduces scheduled report exports.\n\n"
                "Team managers can set up automated recurring schedules: Daily, Weekly on Mondays, or Monthly on the 1st.\n"
                "Reports are automatically compiled in the background and delivered via email to designated management distribution lists.\n"
                "Supported formats in v2.0: CSV and PDF summary report.\n"
                "Real-time AI automated anomaly prediction is not supported in v2.0."
            )
        ]
    )

    # ==========================================
    # Version 3.0 Docs
    # ==========================================
    v3_dir = DOCS_DIR / "v3.0"
    v3_dir.mkdir(parents=True, exist_ok=True)

    create_pdf(
        v3_dir / "enterprise_ai_and_sso.pdf",
        "NexaDesk v3.0 - Enterprise AI Edition",
        [
            (
                "NexaDesk AI Copilot Architecture",
                "NexaDesk v3.0 integrates deep generative AI:\n"
                "- Smart Draft Generator grounded in company documentation.\n"
                "- Ticket Sentiment Analyzer detecting customer frustration.\n"
                "- Instant Thread Summarizer condensing long email chains into three bullets."
            ),
            (
                "Enterprise SAML 2.0 and Multi-Brand SSO",
                "Version 3.0 introduces native SAML 2.0 SSO supporting Okta, Microsoft Entra ID (Azure AD), and Google Workspace."
            )
        ]
    )

    create_docx(
        v3_dir / "nexaflow_studio_guide.docx",
        "NexaDesk v3.0 NexaFlow Studio Guide",
        [
            (
                "NexaFlow Visual Studio",
                "NexaFlow Studio replaces v2.0 linear rules with a visual drag-and-drop workflow canvas."
            ),
            (
                "Unified GraphQL & REST v3 Endpoints",
                "NexaDesk v3.0 deprecates REST API v1. Provides a unified GraphQL endpoint alongside REST API v3."
            )
        ]
    )

    create_txt(
        v3_dir / "pricing_and_quotas.txt",
        "NexaDesk v3.0 Pricing Tiers",
        [
            (
                "Enterprise AI Subscription Plans",
                "Growth Tier: $99 per agent per month, includes NexaFlow Studio and 1,000 AI Copilot credits.\n"
                "Scale Tier: $189 per agent per month, includes SAML SSO, 10 brands, 5,000 AI credits.\n"
                "Enterprise Tier: Custom pricing, unlimited brands, 99.99% uptime SLA.\n\n"
                "Annual Discount: 20% discount on all annual subscriptions."
            )
        ]
    )

    create_md(
        v3_dir / "reporting_and_exports.md",
        "NexaDesk v3.0 Reporting and Analytics",
        [
            (
                "Scheduled and Automated Report Exports in v3.0",
                "NexaDesk v3.0 supports scheduled and automated report exports powered by AI Copilot intelligence.\n\n"
                "Features include:\n"
                "1. Automated Triggered Exports: Exports fire automatically whenever CSAT dips below threshold or SLA breaches exceed 3%.\n"
                "2. Scheduled Recurring Delivery: High-resolution PDF, Excel, and JSON delivered via Slack, Webhooks, or Secure SFTP.\n"
                "3. AI Executive Summaries: Each exported report includes an LLM-synthesized narrative summary highlighting root causes and agent workload bottlenecks."
            )
        ]
    )

    print("\nAll documentation files generated successfully!")


if __name__ == "__main__":
    generate_all()
