"""
Script to generate sample documentation for NexaDesk across versions v1.0, v2.0, and v3.0.
Used for multi-version RAG evaluation and testing.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "backend" / "data" / "documents" / "NexaDesk"


DOCS_CONTENT = {
    "v1.0": {
        "getting_started.md": """# NexaDesk v1.0 - Getting Started Guide

Welcome to NexaDesk v1.0, the lightweight help desk and customer ticketing solution.

## Key Features
- **Email Ingestion:** Converts incoming support emails into trackable support tickets.
- **Agent Dashboard:** Simple list view of pending, open, and closed customer tickets.
- **Manual Assignment:** Team leads manually assign tickets to designated support agents.
- **Knowledge Base (KB):** Basic HTML articles accessible to customers.

## System Requirements
- Modern web browser (Chrome 80+, Firefox 75+, Safari 13+).
- Inbound IMAP/POP3 email account configured for ticket retrieval.

## Support Hours & SLA
- Support is offered Monday to Friday, 9:00 AM - 5:00 PM EST.
- Standard response SLA: 24 hours for Low, 12 hours for Medium, 4 hours for Urgent tickets.
""",
        "ticket_management.md": """# NexaDesk v1.0 - Ticket Management

## Ticket Lifecycle
In NexaDesk v1.0, tickets follow a strict linear status progression:
1. `New` -> Initial state upon email reception.
2. `Open` -> Assigned to an agent.
3. `Pending` -> Awaiting customer response.
4. `Closed` -> Resolved by the agent.

## Limitations in v1.0
- No live chat or instant messaging integrations.
- Tags are static and cannot be created dynamically by agents.
- Maximum attachment size is 5 MB per email.
""",
        "pricing_and_plans.md": """# NexaDesk v1.0 - Pricing and Plans

## Tier Overview
1. **Free Tier:** Up to 2 agents, 100 tickets/month, Community forum support.
2. **Starter Tier ($19/agent/month):** Up to 5 agents, unlimited tickets, email support.
3. **Pro Tier ($49/agent/month):** Up to 15 agents, custom domain, SLA tracking.

*Note: Billing is strictly monthly. Annual billing discounts are not available in v1.0.*
"""
    },
    "v2.0": {
        "getting_started.md": """# NexaDesk v2.0 - Getting Started Guide

Welcome to NexaDesk v2.0, introducing Omnichannel Support and Automation Rules!

## What's New in v2.0
- **Omnichannel Support:** Integrated Live Chat widget for customer websites and a Slack App.
- **Round-Robin Assignment:** Automated ticket routing based on agent capacity.
- **Role-Based Access Control (RBAC):** Introduced Admin, Manager, Agent, and Read-Only roles.
- **Webhook Integrations:** Connect ticket events directly to Zapier, Slack, or internal webhooks.

## Deprecation Notice
- The legacy POP3 email polling engine from v1.0 has been deprecated in favor of real-time Webhook email ingestion (SendGrid/Mailgun).
""",
        "automations_and_routing.md": """# NexaDesk v2.0 - Automations & Routing Rules

## Automation Triggers
NexaDesk v2.0 introduces event-driven trigger rules:
- **On Ticket Created:** Execute actions based on customer domain, ticket priority, or subject keywords.
- **Round-Robin Routing:** Automatically dispatches incoming tickets to online agents.
- **SLA Breach Warnings:** Sends notifications when 75% of SLA resolution time has elapsed.

## SLA Management
- Business hours can now be customized per agent group or timezone.
- Added support for distinct First Response SLA and Total Resolution SLA.
""",
        "pricing_and_plans.md": """# NexaDesk v2.0 - Pricing and Plans

## Revised Tiers
1. **Starter ($29/agent/month):** Up to 5 agents, live chat widget included, 2 automation rules.
2. **Growth ($79/agent/month):** Up to 25 agents, round-robin routing, custom roles, webhook access.
3. **Enterprise ($149/agent/month):** Unlimited agents, custom SLA schedules, dedicated account manager.

*Annual Billing Discount: 15% discount when billed annually.*
"""
    },
    "v3.0": {
        "getting_started.md": """# NexaDesk v3.0 - Getting Started Guide

Welcome to NexaDesk v3.0, the Enterprise AI-Powered Support Platform!

## Key Innovations in v3.0
- **NexaDesk AI Copilot:** Generates suggested responses and ticket summaries using advanced LLM reasoning.
- **NexaFlow Workflow Studio:** Drag-and-drop visual workflow builder replacing legacy v2 automation rules.
- **Multi-Brand Portals:** Host up to 10 distinct customer portals with customized branding under a single account.
- **Enterprise SSO:** Native SAML 2.0, Okta, Azure Active Directory, and Google Workspace SSO.
- **REST API v3 & GraphQL:** Fully typed GraphQL endpoint for high-frequency queries alongside REST v3.

## Backward Compatibility
- v2.0 Automation rules can be auto-migrated into NexaFlow workflows with a single click.
- REST API v1 is officially sunset and returns HTTP 410 Gone.
""",
        "ai_copilot_features.md": """# NexaDesk v3.0 - AI Copilot & Intelligence

## Features
- **Smart Response Generator:** Drafts accurate, brand-aligned responses grounded in company documentation.
- **Ticket Summarization:** Generates instant 3-bullet summaries for long ticket threads.
- **Sentiment & Escalation Predictor:** Detects customer frustration early and auto-escalates to senior tier.
- **Knowledge Gap Detection:** Highlights customer inquiries where KB articles are missing or outdated.

## Privacy & Security
- Customer data is never used to train global public models.
- SOC-2 Type II certified and GDPR compliant data isolation.
""",
        "pricing_and_plans.md": """# NexaDesk v3.0 - Pricing and Plans

## Current Plans
1. **Growth Tier ($99/agent/month):** Full omnichannel, NexaFlow Studio, up to 3 brands, 1,000 AI Copilot credits.
2. **Scale Tier ($189/agent/month):** Advanced analytics, 10 brands, 5,000 AI Copilot credits, SAML SSO.
3. **Enterprise Tier (Custom Pricing):** Unlimited brands, custom AI credit pools, 99.99% uptime SLA, on-premise data residency options.

*Annual Billing Discount: 20% discount on all annual subscriptions.*
"""
    }
}


def generate_documents():
    """Write sample documentation files to their respective version directories."""
    for version, files in DOCS_CONTENT.items():
        v_dir = DOCS_DIR / version
        v_dir.mkdir(parents=True, exist_ok=True)
        print(f"Generating documents for NexaDesk {version} in {v_dir}...")
        for filename, content in files.items():
            file_path = v_dir / filename
            file_path.write_text(content.strip(), encoding="utf-8")
            print(f"  [+] Created: {filename}")
    print("\nAll sample documentation generated successfully!")


if __name__ == "__main__":
    generate_documents()

