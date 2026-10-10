# HarborPay Gateway: project overview and reading paths

Audience: all new team members. Purpose: understand the project and choose an onboarding path.

All companies, people, systems, policies, examples, and tickets in this dataset are fictional training data. HarborPay Technologies operates the fictional HarborPay Gateway. This repository contains a RAG (retrieval-augmented generation) demonstration, not the payment application described here.

## What HarborPay Gateway does

HarborPay Gateway connects a merchant's checkout to a simulated payment provider named MockBridge. A customer provides payment details on the provider's hosted page. HarborPay receives a synthetic token, asks the provider to authorize the payment, and lets an authorized merchant operator capture it. The merchant portal shows payment status and supports refunds.

A merchant is a business selling goods or services. A customer buys from the merchant. MockBridge simulates the external processor. Finance staff compare payment records with simulated settlement reports. QA (quality assurance) checks the behavior; developers build it; business analysts (BAs) clarify rules; managers coordinate delivery.

## Scope and boundaries

HarborPay's example supports INR (Indian rupee) payments, one full manual capture per payment, voiding an unused authorization, and full or partial refunds. Amounts are integer paise: INR 250.00 is 25000 paise.

Multi-currency, foreign exchange, installments, recurring billing, partial capture, multiple captures, real bank transfers, and automated dispute decisions are not supported. Authorization is permission to collect; it is not proof of settlement. All provider behavior is simulated.

## Shared start

Every joiner reads [ownership](02_team_roles_and_ownership.md), completes [access and readiness](03_joiner_checklists_and_access.md), and studies [payment rules](04_payment_terms_and_business_rules.md) and the [payment lifecycle](05_checkout_and_payment_lifecycle.md).

Use your role guide to identify a first task and evidence of completion. Ask your buddy when a rule is unclear; do not invent a financial policy.

## Role reading paths

- **Developer:** shared start -> [architecture](07_architecture_and_service_boundaries.md) -> [setup](08_repositories_local_setup_and_environments.md) -> [API contracts](09_api_contracts_and_error_handling.md) -> [data and idempotency](10_data_model_and_idempotency.md) -> [developer workflow](12_developer_workflow_and_code_review.md).
- **QA engineer:** shared start -> [refunds](06_refunds_settlement_and_reconciliation.md) -> [provider sandbox](11_webhooks_and_provider_sandbox.md) -> [QA strategy](13_qa_strategy_test_data_and_scenarios.md) -> [release verification](17_ci_cd_deployment_and_rollback.md).
- **BA:** shared start -> [refunds and reconciliation](06_refunds_settlement_and_reconciliation.md) -> [API contracts](09_api_contracts_and_error_handling.md) -> [requirements guide](14_ba_requirements_and_acceptance_criteria.md).
- **Manager:** shared start -> [architecture](07_architecture_and_service_boundaries.md) -> [delivery governance](15_manager_delivery_and_release_governance.md) -> [security](16_security_privacy_and_access_controls.md) -> [release](17_ci_cd_deployment_and_rollback.md) -> [incidents](18_monitoring_incidents_and_runbooks.md).

All roles use [known issues](19_jira_known_issues_and_troubleshooting.md) and [FAQ, glossary, and exercises](20_faq_glossary_and_onboarding_exercises.md). The [webhook guide](11_webhooks_and_provider_sandbox.md) explains asynchronous notifications. Security rules apply to every role.

## Using this dataset with the existing RAG demo

The existing Langflow Directory loader can read these flat Markdown files from `sample_data`. The existing flow persona still names the previous company; prompts, exports, old HR demo questions, README, and workshop notes have deliberately not been updated. Those old questions are not supported by this project dataset. Use the project exercises instead.

Replacing files does not remove previously stored vectors. Do not mix the old corpus with HarborPay when evaluating answers. Preserve existing databases; arrange a separate clean persistence location or rebuilt collection in a separately approved configuration step. Do not delete an existing store simply to make the demo run.

The advanced flow's source-path filter `jira` can still select the new known-issues document. A filter for the previous leave-policy filename will not match. Four retrieved chunks may miss evidence in a larger corpus; inspect retrieved passages and cited filenames before accepting an answer. A model can still produce unsupported claims.
