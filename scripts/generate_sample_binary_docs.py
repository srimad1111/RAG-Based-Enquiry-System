"""
Script to generate actual binary sample documents (PDF, DOCX, TXT)
across NexaDesk v1.0, v2.0, and v3.0 with distinct feature behaviors.
"""

from pathlib import Path
import docx
import pymupdf as fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "backend" / "data" / "documents" / "NexaDesk"


def create_pdf(file_path: Path, title: str, sections: list):
    """Generate an actual PDF file with PyMuPDF with structured pages and headings."""
    doc = fitz.open()
    for sec_title, sec_text in sections:
        page = doc.new_page(width=595, height=842)  # A4 size
        # Header
        page.insert_text(fitz.Point(50, 60), title, fontsize=11, color=(0.4, 0.4, 0.4))
        # Section Heading
        page.insert_text(fitz.Point(50, 100), sec_title, fontsize=16, color=(0.1, 0.1, 0.6))
        # Body text
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


def generate_all():
    print("Generating real PDF, DOCX, and TXT documentation for NexaDesk...")

    # ==========================================
    # Version 1.0 Sample Binary Docs
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
                "Attachment Limitation: Incoming emails with attachments exceeding 5 MB will be rejected with an automated bounce notice.\n"
                "Manual assignment is required for all imported emails."
            ),
            (
                "SLA Policy and Resolution Deadlines",
                "NexaDesk v1.0 defines fixed, non-customizable SLA resolution targets:\n\n"
                "1. Urgent Severity: 4 hours total resolution deadline.\n"
                "2. Medium Severity: 12 hours total resolution deadline.\n"
                "3. Low Severity: 24 hours total resolution deadline.\n\n"
                "Note on Business Hours: In v1.0, SLA clocks run continuously 24/7. Support for holiday calendars "
                "or business-hour exclusions is not available until future releases."
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
                "- Administrator: Full system access, email mailbox settings, user provisioning, and raw log viewing.\n"
                "- Agent: Can view assigned tickets, post public replies, add internal notes, and mark tickets as closed.\n\n"
                "Granular permissions, custom role creation, or view-only auditor roles are not supported in version 1.0."
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
                "Starter Tier: $19 per agent per month, unlimited tickets, standard email support.\n"
                "Pro Tier: $49 per agent per month, custom email domain, priority queue.\n\n"
                "Billing Policy: All billing is month-to-month. Annual pre-payment discounts are not offered in v1.0."
            )
        ]
    )

    # ==========================================
    # Version 2.0 Sample Binary Docs
    # ==========================================
    v2_dir = DOCS_DIR / "v2.0"
    v2_dir.mkdir(parents=True, exist_ok=True)

    create_pdf(
        v2_dir / "omnichannel_and_webhooks.pdf",
        "NexaDesk v2.0 - Technical Documentation",
        [
            (
                "Deprecation of POP3 and Real-Time Webhooks",
                "Important Architectural Change in v2.0:\n\n"
                "The legacy POP3 polling worker from v1.0 is officially DEPRECATED.\n"
                "Incoming emails must now be routed via SendGrid Inbound Parse or Mailgun HTTP Webhooks, "
                "providing instant, sub-second ticket creation.\n"
                "Maximum attachment size has been increased from 5 MB to 25 MB.\n"
                "Customers still relying on POP3 must upgrade their inbound MX records to webhooks."
            ),
            (
                "Live Chat Widget and Slack Integration",
                "NexaDesk v2.0 introduces omnichannel communication:\n\n"
                "- Web Live Chat Widget: Embeddable JavaScript snippet for customer portals.\n"
                "- Slack Support App: Bi-directional sync allowing agents to respond to customer inquiries "
                "directly from dedicated Slack channels without opening the web dashboard."
            )
        ]
    )

    create_docx(
        v2_dir / "rbac_and_round_robin.docx",
        "NexaDesk v2.0 Advanced Routing & Roles",
        [
            (
                "Enhanced RBAC Roles",
                "NexaDesk v2.0 expands user roles to four distinct tiers:\n"
                "1. Admin: Complete control over billing, integrations, and global settings.\n"
                "2. Manager: Can configure round-robin rules, reassign any agent ticket, and inspect SLA analytics.\n"
                "3. Agent: Answers customer tickets and manages individual status (Online, Busy, Away).\n"
                "4. Read-Only Viewer: Intended for external auditors and executives."
            ),
            (
                "Automated Round-Robin Routing",
                "In v2.0, manual ticket assignment is replaced by automated round-robin dispatch.\n"
                "Incoming tickets are assigned to the online agent with the lowest number of currently open tickets.\n"
                "Routing rules can be filtered by tag, priority, or customer language."
            )
        ]
    )

    create_txt(
        v2_dir / "pricing_and_quotas.txt",
        "NexaDesk v2.0 Pricing Tiers",
        [
            (
                "Revised Subscription Plans",
                "Starter Tier: $29 per agent per month, includes Live Chat widget, up to 5 agents.\n"
                "Growth Tier: $79 per agent per month, includes Round-Robin routing and Slack integration.\n"
                "Enterprise Tier: $149 per agent per month, custom SLA schedules, dedicated account manager.\n\n"
                "Annual Discount: 15% discount applies when paying annually upfront."
            )
        ]
    )

    # ==========================================
    # Version 3.0 Sample Binary Docs
    # ==========================================
    v3_dir = DOCS_DIR / "v3.0"
    v3_dir.mkdir(parents=True, exist_ok=True)

    create_pdf(
        v3_dir / "enterprise_ai_and_sso.pdf",
        "NexaDesk v3.0 - Enterprise AI Edition",
        [
            (
                "NexaDesk AI Copilot Architecture",
                "NexaDesk v3.0 integrates deep generative AI directly into the agent response editor:\n\n"
                "- Smart Draft Generator: Generates grounded response suggestions using company documentation.\n"
                "- Ticket Sentiment Analyzer: Detects escalating customer frustration and alerts shift managers.\n"
                "- Instant Thread Summarizer: Condenses 20+ message email chains into three bullet points.\n"
                "AI responses must be reviewed and approved by a human agent before sending."
            ),
            (
                "Enterprise SAML 2.0 and Multi-Brand SSO",
                "Version 3.0 introduces Enterprise Identity Management:\n\n"
                "- Native SAML 2.0 integration supporting Okta, Microsoft Entra ID (Azure AD), and Google Workspace.\n"
                "- Just-In-Time (JIT) user provisioning with SCIM 2.0.\n"
                "- Multi-Brand Customer Portals: Manage up to 10 distinct brands with separate styling and domain names."
            )
        ]
    )

    create_docx(
        v3_dir / "nexaflow_studio_guide.docx",
        "NexaDesk v3.0 NexaFlow Studio Guide",
        [
            (
                "NexaFlow Visual Studio",
                "NexaFlow Studio replaces the linear round-robin rules from v2.0 with a visual drag-and-drop builder.\n"
                "Admins can construct conditional branching nodes, invoke external REST webhooks, and trigger AI sentiment analysis.\n"
                "v2.0 rules are automatically migrated to NexaFlow workflows upon upgrading."
            ),
            (
                "Unified GraphQL & REST v3 Endpoints",
                "NexaDesk v3.0 deprecates REST API v1 (HTTP 410 Gone).\n"
                "Developers can query the unified GraphQL endpoint (/graphql) for high-frequency queries "
                "or utilize REST API v3 (/api/v3) with complete OpenAPI 3.1 specifications."
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
                "Enterprise Tier: Custom pricing, unlimited brands, private VPC deployment, 99.99% uptime SLA.\n\n"
                "Annual Discount: 20% discount on all annual subscriptions."
            )
        ]
    )

    print("\nAll binary and text sample documentation generated successfully!")


if __name__ == "__main__":
    generate_all()
