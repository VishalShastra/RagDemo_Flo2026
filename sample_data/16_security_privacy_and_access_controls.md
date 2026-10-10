# HarborPay Gateway: security, privacy, and access controls

Audience: everyone. Purpose: set safe data and permission boundaries for onboarding.

All security controls and identities are fictional training data. HarborPay has no claimed certification. This dataset is not proof of Payment Card Industry Data Security Standard (PCI DSS) compliance.

## Data boundaries

Use synthetic merchants, orders, tokens, and monetary amounts only. Do not use real card numbers, primary account numbers (PANs), card verification values (CVVs), bank-account details, personal identifiers, or customer records in training.

Provider-hosted collection keeps raw card details outside HarborPay. Synthetic tokens are still treated as sensitive in example logs. Never copy real production payloads into a test, issue, chat, or public AI assistant. Sanitization means deliberately removing sensitive values, not merely renaming a file.

## Authentication and merchant authorization

An authenticated identity must be active and have the required permission. Every payment/refund read or mutation checks the authenticated merchant against resource ownership. Return a nonrevealing not-found response for another merchant's object.

Example portal roles:

| Role | Allowed example actions |
|---|---|
| Merchant Viewer | Read own payments/refunds |
| Merchant Operator | Viewer actions plus create, authorize, and capture |
| Merchant Supervisor | Operator actions plus void and refund |
| Platform Support | Approved diagnostics; no merchant money-operation permission by default |

Job titles such as QA, BA, or Manager do not automatically confer these portal roles. Tests use dedicated synthetic role fixtures. Financial action permissions must be enforced by the server, not only by hiding buttons.

## Secrets and transport

Store credentials and webhook keys in approved secret storage. Configuration uses references such as `WEBHOOK_SECRET_REF`, not inline secret values. Never commit keys, share logins, or paste credentials into documentation.

Use transport layer security (TLS) for nonlocal traffic. Verify webhook authenticity and timestamp freshness. Rotate keys through the Platform/Security process; do not disable signature checks to fix test failures.

## Safe logs and audit

Operational logs include trace ID, payment/refund/operation IDs, outcome code, and environment. Redact credentials, tokens, card data, and raw signed request bodies. Access to logs is role-limited.

Audit records include actor, action, object, timestamp, and state change. Preserve evidence of access, refunds, release approvals, and investigations. Do not edit historical audit records to hide a mistake.

## Access and incidents

Standard sandbox access requires line manager approval. Privileged/production access additionally requires Leena's approval and a defined expiry. Omar provisions access; the approver must not approve their own request.

Report suspected exposure or unauthorized financial action immediately to Leena and `#hpg-incidents`. Include a sanitized trace ID and description. Restrict the unsafe path with Platform coordination, preserve evidence, and avoid copying leaked values into the report. Do not wait for certainty before raising a potential security incident.

Read the [joiner checklist](03_joiner_checklists_and_access.md) and [incident runbooks](18_monitoring_incidents_and_runbooks.md). Production governance would require a separate reviewed control framework; the local RAG server does not implement payment-project authorization.
