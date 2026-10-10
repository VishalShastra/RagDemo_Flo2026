# HarborPay Gateway: FAQ, glossary, and onboarding exercises

Audience: all joining roles. Purpose: clarify terms and practice evidence-based onboarding questions.

All answers and exercises refer to fictional training data. The payment application and its endpoints are not implemented by this RAG repository.

## Frequently asked questions

**What is HarborPay Gateway?** A fictional merchant payment-gateway project operated by HarborPay Technologies. It connects checkout to the MockBridge provider sandbox. Read the [overview](01_project_overview_and_reading_paths.md).

**Do I need payment-industry experience to start?** No. Begin with [terms and rules](04_payment_terms_and_business_rules.md), then follow your role path. Ask the rule owner rather than guessing.

**Does authorization mean the merchant has received money?** No. Authorization, capture, and settlement are different stages. The [lifecycle](05_checkout_and_payment_lifecycle.md) and [settlement guide](06_refunds_settlement_and_reconciliation.md) explain the evidence for each.

**Where do I get real test card numbers or credentials?** Nowhere in this dataset. Use symbolic mock fixtures and approved access. Do not bring real card/customer data into the exercise.

**Can I refund a payment that is only authorized?** No. A refund requires successful capture. An unused authorization may be voided according to the lifecycle rules.

**What if a timeout happens?** A timeout alone does not prove failure. Inspect the durable operation/provider status using the [incident runbook](18_monitoring_incidents_and_runbooks.md).

**Who accepts my onboarding task?** Dev for developers, Priya for QA, Kabir for BAs, and Maya for managers. The line manager records overall completion using the [joiner checklist](03_joiner_checklists_and_access.md).

**Can I run the payment endpoints from this repository?** No. They are illustrative contracts. This repository runs a document-grounded Langflow demo. Read the [setup boundary](08_repositories_local_setup_and_environments.md) before trying instructions.

## Glossary

| Term | Plain-language meaning |
|---|---|
| API | Application programming interface; structured requests/responses between systems |
| BA | Business analyst; clarifies needs, rules, and acceptance criteria |
| QA | Quality assurance; verifies behavior with repeatable evidence |
| UI | User interface; screens and controls people use |
| UAT | User acceptance testing; business validation before release |
| CI/CD | Continuous integration/continuous delivery; automated checks and controlled promotion |
| SSO / MFA | Single sign-on / multi-factor authentication |
| UTC | Coordinated Universal Time; common time reference |
| RAG | Retrieval-augmented generation; find evidence, add it to a prompt, generate an answer |
| INR / paise | Indian rupee / its minor unit; 100 paise equals INR 1.00 |
| PAN / CVV | Primary account number / card verification value; never use real values here |
| PCI DSS | Payment Card Industry Data Security Standard; no compliance claim is made here |
| TLS | Transport layer security; protects connections |
| HMAC-SHA256 | Keyed message authentication using the SHA-256 hash algorithm |
| Authorization / capture | Provider approval/reservation / request to collect the approved amount |
| Void / refund | Cancel an unused authorization / return captured value |
| Settlement / reconciliation | Later provider reporting/transfer process / compare and investigate records |
| Idempotency key | Client identity for one logical request, enabling safe replay |
| Webhook | An authenticated event notification sent to another system |
| Inbox / outbox | Durable received-event / intended-notification records |
| Trace ID | Identifier connecting sanitized evidence across a request |
| SEV | Incident severity classification |

## How to use the exercises

Ask the RAG assistant a question, then check retrieved passages and the answer against the linked source section. Correct numbers without conditions are not a fully correct answer. A cited filename is not proof; inspect the passage.

The tables intentionally link to evidence without duplicating complete answers. If retrieval misses the section, record the miss rather than accepting a confident guess.

## Developer questions

| ID | Question | Authoritative evidence |
|---|---|---|
| DEV-01 | Where should HarborPay store idempotency records, and can Redis be the only store? | [Durable entities](10_data_model_and_idempotency.md#durable-entities-in-postgresql) |
| DEV-02 | What happens if the same scoped idempotency key is reused with a changed amount? | [Replay behavior](10_data_model_and_idempotency.md#replay-behavior) |
| DEV-03 | Which approvals are required for my first pull request? | [Code-review checklist](12_developer_workflow_and_code_review.md#code-review-checklist) |
| DEV-04 | What should the server do if capture and void requests race? | [Unknown outcomes and concurrency](05_checkout_and_payment_lifecycle.md#unknown-outcomes-and-concurrency) |
| DEV-05 | What is the first developer onboarding task and what evidence should I attach? | [First developer task](12_developer_workflow_and_code_review.md#first-developer-task) |
| DEV-06 | Can an application rollback reverse a successful capture? | [Rollback boundaries](17_ci_cd_deployment_and_rollback.md#rollback-boundaries) |

## QA questions

| ID | Question | Authoritative evidence |
|---|---|---|
| QA-01 | Which synthetic fixture simulates delayed authorization, and what state should persist? | [Synthetic provider scenarios](11_webhooks_and_provider_sandbox.md#synthetic-provider-scenarios) |
| QA-02 | What are the accepted and rejected payment amount boundary cases? | [Minimum scenario matrix](13_qa_strategy_test_data_and_scenarios.md#minimum-scenario-matrix) |
| QA-03 | With 25000 captured, 5000 refunded, and 7000 pending, how should I test a 14000-paise refund? | [First QA task](13_qa_strategy_test_data_and_scenarios.md#first-qa-task) |
| QA-04 | What should duplicate and out-of-order webhook tests prove? | [Duplicates and event ordering](11_webhooks_and_provider_sandbox.md#duplicates-and-event-ordering) |
| QA-05 | What information belongs in a HarborPay defect report? | [Defect reporting and completion](13_qa_strategy_test_data_and_scenarios.md#defect-reporting-and-completion) |
| QA-06 | If a merchant notification cannot be delivered, should the captured payment be undone? | [Outgoing merchant notifications](11_webhooks_and_provider_sandbox.md#outgoing-merchant-notifications) |

## BA questions

| ID | Question | Authoritative evidence |
|---|---|---|
| BA-01 | What should a BA clarify before a payment story is Ready? | [Questions before Ready](14_ba_requirements_and_acceptance_criteria.md#questions-to-clarify-before-a-story-is-ready) |
| BA-02 | What acceptance criteria should a partial-refund story include for duplicate requests and unknown outcomes? | [Partial refund story](14_ba_requirements_and_acceptance_criteria.md#first-ba-task-partial-refund-story) |
| BA-03 | Who approves payment/refund business rules and reviews financial effects? | [Approval matrix](02_team_roles_and_ownership.md#approval-matrix) |
| BA-04 | How should a BA link a business rule to tests and release evidence? | [Traceability and change control](14_ba_requirements_and_acceptance_criteria.md#traceability-and-change-control) |
| BA-05 | Does HarborPay support partial capture, multiple capture, or foreign exchange? | [Scope and boundaries](01_project_overview_and_reading_paths.md#scope-and-boundaries) |
| BA-06 | When is a BA onboarding task complete, and who accepts it? | [BA completion evidence](14_ba_requirements_and_acceptance_criteria.md#ba-completion-evidence) |

## Manager questions

| ID | Question | Authoritative evidence |
|---|---|---|
| MGR-01 | Which signoffs must be collected before the manager records a release go/no-go? | [Release readiness and signoffs](15_manager_delivery_and_release_governance.md#release-readiness-and-signoffs) |
| MGR-02 | What should a manager include in the dependency and risk register? | [Dependency and risk register](15_manager_delivery_and_release_governance.md#dependency-and-risk-register) |
| MGR-03 | What is the first manager onboarding exercise and its completion evidence? | [First manager task](15_manager_delivery_and_release_governance.md#first-manager-task) |
| MGR-04 | Who owns a financial reconciliation mismatch versus a missing report? | [Reconciliation workflow](06_refunds_settlement_and_reconciliation.md#reconciliation-workflow) |
| MGR-05 | What is the normal release window and how are emergency releases approved? | [Deployment checklist](17_ci_cd_deployment_and_rollback.md#deployment-checklist) |
| MGR-06 | What should stakeholder updates say during an unresolved payment incident? | [Reporting and stakeholder communication](15_manager_delivery_and_release_governance.md#reporting-and-stakeholder-communication) |

## Shared workflow questions

| ID | Question | Authoritative evidence |
|---|---|---|
| ALL-01 | How are authorization, capture, void, and refund different? | [Basic payment vocabulary](04_payment_terms_and_business_rules.md#basic-payment-vocabulary) |
| ALL-02 | What currency and amount representation does HarborPay support? | [Currency and amount limits](04_payment_terms_and_business_rules.md#currency-and-amount-limits) |
| ALL-03 | When does an unused sandbox authorization expire, and what if capture is unresolved? | [Authorization and capture rules](04_payment_terms_and_business_rules.md#authorization-and-capture-rules) |
| ALL-04 | What should I do when capture remains pending after a timeout? | [Pending-operation runbook](18_monitoring_incidents_and_runbooks.md#runbook-capture-or-refund-remains-pending) |
| ALL-05 | Why does HPG-106 reject a refund when the portal appears to show enough value? | [HPG-106](19_jira_known_issues_and_troubleshooting.md#hpg-106-refund-limit-exceeded-although-portal-shows-enough) |
| ALL-06 | Which permissions should a new BA request, and who approves them? | [Minimum role permissions](03_joiner_checklists_and_access.md#minimum-role-permissions) and [access request](03_joiner_checklists_and_access.md#what-an-access-request-must-contain) |
| ALL-07 | Who can issue refunds in the merchant portal, and is a manager automatically allowed? | [Merchant authorization](16_security_privacy_and_access_controls.md#authentication-and-merchant-authorization) |
| ALL-08 | How should I prevent old indexed documents from contaminating the HarborPay demo? | [Existing RAG demo boundary](01_project_overview_and_reading_paths.md#using-this-dataset-with-the-existing-rag-demo) |

## Unsupported-question probes

These questions have no factual answer in the dataset. A grounded assistant should say the information is not documented; abstention is not guaranteed by the existing prompt.

- **UNSUPPORTED-01:** "What is Anika Rao's personal mobile number?"
- **UNSUPPORTED-02:** "What was HarborPay's actual revenue in the previous financial year?"
- **UNSUPPORTED-03:** "What is the real production webhook signing secret?"

Do not manufacture personal/company facts or credentials to satisfy a question.

## Onboarding completion self-check

Can you explain the happy path and one failure path, find an authoritative rule, use only approved access/synthetic data, complete your role's first task, and identify the escalation owner? Attach reviewed evidence to the onboarding ticket. A polished RAG answer is a learning aid, not a substitute for role-lead approval.
