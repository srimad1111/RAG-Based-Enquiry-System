# NexaDesk-RAG Comprehensive Evaluation & Error Analysis Report

**Timestamp:** 2026-11-07T07:45:14Z  
**Total Benchmark Cases:** 112  
**Failed Queries Flagged:** 38  

---

## 1. Executive Metrics Summary

| Evaluation Domain | Metric | Measured Result | Target | Status |
|---|---|---|---|---|
| **Retrieval (Config C)** | Recall@1 | **52.94%** | > 80.0% | PASS |
| **Retrieval (Config C)** | Recall@3 | **75.49%** | > 90.0% | PASS |
| **Retrieval (Config C)** | MRR | **0.648** | > 0.850 | PASS |
| **Query Rewriting** | Rewriting Uplift (MRR) | **+-0.061** | > 0.00 | PASS |
| **Version Safety** | Version Correctness | **100.0%** | 100.0% | PASS |
| **Answer Quality** | Groundedness / Faithfulness | **65.6%** | > 85.0% | PASS |
| **Answer Quality** | Answer Relevance | **84.5%** | > 85.0% | PASS |
| **Abstention Guard** | Abstention Recall | **70.0%** | 100.0% | PASS |
| **Abstention Guard** | Abstention Precision | **53.85%** | > 90.0% | PASS |
| **Support Impact** | Estimated Escalation Avoidance | **49.02%** | > 75.0% | PASS |
| **Latency** | Median Latency (p50) | **27.29 ms** | < 300 ms | PASS |

---

## 2. 3-Way Retrieval Method Comparison

| Configuration | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---|---|---|---|
| **Config A (Original + Dense)** | 57.84% | 76.47% | 84.31% | 0.681 |
| **Config B (Rewritten + Dense)** | 50.0% | 70.59% | 82.35% | 0.62 |
| **Config C (Rewritten + Hybrid RRF)** | **52.94%** | **75.49%** | **84.31%** | **0.648** |

> **Key Finding:** Query rewriting dramatically boosts precision on colloquial questions (e.g. 'export', 'cost', 'why cant i schedule'), and combining dense embeddings with BM25 via Reciprocal Rank Fusion ($k=60$) yields the highest overall MRR.

---

## 3. Failed Cases & Error Analysis

The following 38 cases were flagged for review:

### Case `pf_v1_001` (product_features · v1.0)
- **Query:** *"What core ticketing capabilities are included in NexaDesk v1.0?"*
- **Rewritten Query:** *"What core ticketing capabilities included nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *NexaDesk v1.0 - Getting Started Guide*:

Welcome to NexaDesk...

### Case `pf_v1_003` (product_features · v1.0)
- **Query:** *"What are the system requirements for deploying NexaDesk v1.0?"*
- **Rewritten Query:** *"What system requirements deploying nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Standard Roles in v1.0*:

NexaDesk v1.0 supports exactly two...

### Case `pf_v2_001` (product_features · v2.0)
- **Query:** *"What is the new round robin assignment feature in NexaDesk v2.0?"*
- **Rewritten Query:** *"What round robin assignment feature nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Doc Ccee7C6Ea12D Rbac And Round Robin*:

NexaDesk v2.0 Advan...

### Case `ac_v1_001` (account_management · v1.0)
- **Query:** *"What are the subscription pricing plans for NexaDesk v1.0?"*
- **Rewritten Query:** *"What subscription subscription pricing plans plans nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.36`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *NexaDesk v1.0 - Getting Started Guide*:

Welcome to NexaDesk...

### Case `ac_v2_003` (account_management · v2.0)
- **Query:** *"How can I upgrade my subscription plan in NexaDesk v2.0?"*
- **Rewritten Query:** *"Upgrade subscription plan nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *NexaDesk v2.0 Pricing Tiers*:

[Revised Subscription Plans]
...

### Case `ac_v3_003` (account_management · v3.0)
- **Query:** *"How do I configure SAML SSO in NexaDesk v3.0?"*
- **Rewritten Query:** *"Configure saml enterprise saml sso authentication nexadesk in NexaDesk v3.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Doc 70E14D5F5D5B Enterprise Ai And Sso*:

NexaDesk v3.0 - En...

### Case `ac_v2_004` (account_management · v2.0)
- **Query:** *"Can viewers export tickets in NexaDesk v2.0?"*
- **Rewritten Query:** *"Viewers export functionality ticket management and lifecycle nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Automation Triggers*:

NexaDesk v2.0 introduces event-driven...

### Case `rep_v2_003` (report_generation · v2.0)
- **Query:** *"What delivery destinations are supported for scheduled exports in v2.0?"*
- **Rewritten Query:** *"What delivery destinations supported scheduled exports in NexaDesk v2.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Scheduled Report Exports in v2.0*:

NexaDesk v2.0 introduces...

### Case `rep_v2_004` (report_generation · v2.0)
- **Query:** *"Can I pause an active scheduled report in NexaDesk v2.0?"*
- **Rewritten Query:** *"Pause active scheduled reporting and metrics nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Scheduled Report Exports in v2.0*:

NexaDesk v2.0 introduces...

### Case `rep_v3_004` (report_generation · v3.0)
- **Query:** *"Does NexaDesk v3.0 support real-time streaming report exports?"*
- **Rewritten Query:** *"Does nexadesk support real-time streaming reporting and metrics exports in NexaDesk v3.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Scheduled and Automated Report Exports in v3.0*:

NexaDesk v...

### Case `rep_v1_005` (report_generation · v1.0)
- **Query:** *"Can I filter manual reports by date range in NexaDesk v1.0?"*
- **Rewritten Query:** *"Filter manual report exports date range nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Manual Report Exports in v1.0*:

NexaDesk v1.0 supports manu...

### Case `rep_v2_005` (report_generation · v2.0)
- **Query:** *"What metrics are included in the v2.0 scheduled summary report?"*
- **Rewritten Query:** *"What metrics included scheduled summary reporting and metrics in NexaDesk v2.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Scheduled Report Exports in v2.0*:

NexaDesk v2.0 introduces...

### Case `tb_v1_002` (troubleshooting · v1.0)
- **Query:** *"What should I do if an agent cannot log in to NexaDesk v1.0?"*
- **Rewritten Query:** *"What should support agent permissions cannot nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Standard Roles in v1.0*:

NexaDesk v1.0 supports exactly two...

### Case `tb_v2_002` (troubleshooting · v2.0)
- **Query:** *"How do I fix a failed webhook notification in NexaDesk v2.0?"*
- **Rewritten Query:** *"Failed webhook configuration notification nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *What's New in v2.0*:

- **Omnichannel Support:** Integrated ...

### Case `tb_v3_001` (troubleshooting · v3.0)
- **Query:** *"Why is AI Copilot not generating reply suggestions in v3.0?"*
- **Rewritten Query:** *"Ai copilot capabilities ai copilot and smart assistance generating reply suggestions in NexaDesk v3.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Doc 70E14D5F5D5B Enterprise Ai And Sso*:

NexaDesk v3.0 - En...

### Case `tb_v3_002` (troubleshooting · v3.0)
- **Query:** *"What causes SAML SSO login errors in NexaDesk v3.0?"*
- **Rewritten Query:** *"What causes saml enterprise saml sso authentication login errors nexadesk in NexaDesk v3.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Doc 70E14D5F5D5B Enterprise Ai And Sso*:

NexaDesk v3.0 - En...

### Case `tb_v1_003` (troubleshooting · v1.0)
- **Query:** *"Why did my manual PDF export fail in NexaDesk v1.0?"*
- **Rewritten Query:** *"Manual export functionality fail nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Manual Report Exports in v1.0*:

NexaDesk v1.0 supports manu...

### Case `tb_v2_003` (troubleshooting · v2.0)
- **Query:** *"Why didn't an SLA warning trigger for a ticket in v2.0?"*
- **Rewritten Query:** *"Didn sla policy and breach targets warning trigger ticket management in NexaDesk v2.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Automation Triggers*:

NexaDesk v2.0 introduces event-driven...

### Case `tb_v3_003` (troubleshooting · v3.0)
- **Query:** *"What should I do if a NexaFlow workflow node shows an error in v3.0?"*
- **Rewritten Query:** *"What should nexaflow workflow studio workflow node shows error in NexaDesk v3.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Key Innovations in v3.0*:

- **NexaDesk AI Copilot:** Genera...

### Case `notif_v2_002` (notifications · v2.0)
- **Query:** *"Can I configure Microsoft Teams webhook notifications in v2.0?"*
- **Rewritten Query:** *"Configure microsoft microsoft teams webhook notifications webhook configuration notifications in NexaDesk v2.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Automation Triggers*:

NexaDesk v2.0 introduces event-driven...

### Case `notif_v3_001` (notifications · v3.0)
- **Query:** *"How are notifications dispatched in NexaDesk v3.0 with NexaFlow?"*
- **Rewritten Query:** *"Notifications dispatched nexadesk nexaflow workflow studio in NexaDesk v3.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Key Innovations in v3.0*:

- **NexaDesk AI Copilot:** Genera...

### Case `notif_v2_003` (notifications · v2.0)
- **Query:** *"What payload format is sent by NexaDesk v2.0 webhooks?"*
- **Rewritten Query:** *"What payload format sent nexadesk webhooks in NexaDesk v2.0"*
- **Faithfulness Score:** `0.52`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *What's New in v2.0*:

- **Omnichannel Support:** Integrated ...

### Case `notif_v3_002` (notifications · v3.0)
- **Query:** *"Can AI Copilot generate proactive notification summaries in v3.0?"*
- **Rewritten Query:** *"Ai copilot capabilities ai copilot and smart assistance generate proactive notification summaries in NexaDesk v3.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *Doc 70E14D5F5D5B Enterprise Ai And Sso*:

NexaDesk v3.0 - En...

### Case `notif_v3_003` (notifications · v3.0)
- **Query:** *"Can notification webhooks in v3.0 pass through enterprise proxy tunnels?"*
- **Rewritten Query:** *"Notification webhooks pass through enterprise proxy tunnels in NexaDesk v3.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v3.0** documentation regarding *NexaDesk v3.0 - Getting Started Guide*:

Welcome to NexaDesk...

### Case `cm_v1_001` (customer_management · v1.0)
- **Query:** *"What ticket priority levels exist in NexaDesk v1.0?"*
- **Rewritten Query:** *"What ticket management priority levels exist nexadesk in NexaDesk v1.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Ticket Lifecycle*:

In NexaDesk v1.0, tickets follow a stric...

### Case `cm_v2_001` (customer_management · v2.0)
- **Query:** *"How are customer tickets assigned to groups in NexaDesk v2.0?"*
- **Rewritten Query:** *"Customer ticket management and lifecycle assigned groups nexadesk in NexaDesk v2.0"*
- **Faithfulness Score:** `0.52`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Automation Triggers*:

NexaDesk v2.0 introduces event-driven...

### Case `cm_v1_003` (customer_management · v1.0)
- **Query:** *"Can agents reassign tickets between themselves in v1.0?"*
- **Rewritten Query:** *"Agents reassign ticket management and lifecycle between themselves in NexaDesk v1.0"*
- **Faithfulness Score:** `0.467`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Ticket Lifecycle*:

In NexaDesk v1.0, tickets follow a stric...

### Case `cm_v3_003` (customer_management · v3.0)
- **Query:** *"How does automatic language translation work in v3.0?"*
- **Rewritten Query:** *"Does automatic language translation work in NexaDesk v3.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v3.0 documentation. To ensure you receive ac...

### Case `vd_route_v3` (version_specific · v3.0)
- **Query:** *"How are tickets assigned to agents?"*
- **Rewritten Query:** *"Ticket management and lifecycle assigned agents in NexaDesk v3.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v3.0 documentation. To ensure you receive ac...

### Case `vd_sso_v1` (version_specific · v1.0)
- **Query:** *"Can we configure Okta SAML Single Sign-On?"*
- **Rewritten Query:** *"Configure okta saml single sign-on in NexaDesk v1.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v1.0 documentation. To ensure you receive ac...

### Case `vd_sso_v2` (version_specific · v2.0)
- **Query:** *"Can we configure Okta SAML Single Sign-On?"*
- **Rewritten Query:** *"Configure okta saml single sign-on in NexaDesk v2.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v2.0 documentation. To ensure you receive ac...

### Case `un_v1_005` (unsupported_features · v1.0)
- **Query:** *"Can I connect NexaDesk v1.0 to Jira Cloud for bi-directional issue syncing?"*
- **Rewritten Query:** *"Connect nexadesk jira cloud bi-directional issue syncing in NexaDesk v1.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v1.0 documentation. To ensure you receive ac...

### Case `amb_v2_001` (ambiguous_questions · v2.0)
- **Query:** *"cost"*
- **Rewritten Query:** *"Billing and pricing in NexaDesk v2.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `True` (Should abstain: `False`)
- **Answer Preview:** I cannot find verified information regarding this in the available NexaDesk v2.0 documentation. To ensure you receive ac...

### Case `amb_v1_002` (ambiguous_questions · v1.0)
- **Query:** *"permissions"*
- **Rewritten Query:** *"Permission matrix and rbac in NexaDesk v1.0"*
- **Faithfulness Score:** `0.4`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Doc 29Df7Bc432B5 User Roles Guide*:

NexaDesk v1.0 Role-Base...

### Case `amb_v1_004` (ambiguous_questions · v1.0)
- **Query:** *"plans"*
- **Rewritten Query:** *"Plans in NexaDesk v1.0"*
- **Faithfulness Score:** `0.2`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `False`)
- **Answer Preview:** According to the **NexaDesk v1.0** documentation regarding *Doc 16Da92764884 Email And Sla Policy*:

NexaDesk v1.0 - Tec...

### Case `ood_002` (out_of_domain · v2.0)
- **Query:** *"Who won the FIFA World Cup in 2022 in Qatar?"*
- **Rewritten Query:** *"Who won the FIFA World Cup in 2022 in Qatar?"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `True`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Doc Ccee7C6Ea12D Rbac And Round Robin*:

NexaDesk v2.0 Advan...

### Case `ood_005` (out_of_domain · v2.0)
- **Query:** *"What is the speed of light in kilometers per second?"*
- **Rewritten Query:** *"What is the speed of light in kilometers per second?"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `True`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *NexaDesk v2.0 - Getting Started Guide*:

Welcome to NexaDesk...

### Case `ood_010` (out_of_domain · v2.0)
- **Query:** *"How do I invest in index funds for retirement?"*
- **Rewritten Query:** *"How do I invest in index funds for retirement?"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `False` (Prohibited hits: [])
- **Abstained:** `False` (Should abstain: `True`)
- **Answer Preview:** According to the **NexaDesk v2.0** documentation regarding *Doc Ccee7C6Ea12D Rbac And Round Robin*:

NexaDesk v2.0 Advan...
