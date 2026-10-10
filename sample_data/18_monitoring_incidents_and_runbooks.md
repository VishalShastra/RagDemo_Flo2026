# HarborPay Gateway: monitoring, incidents, and runbooks

Audience: Platform, developers, QA, Finance, and managers. Purpose: diagnose failures without creating duplicate financial operations.

All dashboards, thresholds, schedules, and incident procedures are fictional training data.

## Useful signals

Monitor provider technical error rate separately from business decline rate. A customer decline can be a valid outcome. Track authorization/capture/refund latency, pending-operation age, webhook failures, outbox backlog, database readiness, and reconciliation mismatches.

Sandbox alert examples: provider technical errors above 5% for five minutes with at least 20 requests; any money operation pending longer than ten minutes; any nonzero reconciliation mismatch after comparison. These are investigation triggers, not proof an operation failed.

Use trace ID -> payment/refund ID -> operation ID -> provider operation ID to connect evidence. Redacted logs and audit summaries are safer than full request dumps.

## Incident severity and ownership

| Severity | Example | Coordinator |
|---|---|---|
| SEV1 | Suspected duplicate financial action or sensitive-data exposure | Omar coordinates response; Ravi handles money evidence; Leena handles exposure |
| SEV2 | Widespread blocked checkout or growing unresolved operations | Omar |
| SEV3 | Limited sandbox failure with safe workaround | Relevant role lead |

SEV means severity. Report to `#hpg-incidents` immediately with environment, symptom, sanitized IDs, impact, and actions already taken. Maya handles stakeholder updates; Dev supports code investigation; Priya validates recovery.

## Runbook: capture or refund remains pending

1. Read the durable operation and its provider operation ID using approved diagnostic access.
2. Check verified provider status and any inbox event; do not interpret a timeout as failure.
3. Apply a legal transition through the normal recovery worker, with audit evidence.
4. If the outcome is still unclear, keep pending state/reservation and escalate to Omar and Ravi.
5. Block conflicting money operations until resolution. Never create a new key, delete the record, or retry with a different payment to "unstick" it.

## Runbook: merchant did not receive an event

Check outbox event ID, destination configuration, response code, attempt count, and failed-delivery queue. Notify Omar after the initial attempt and three bounded retries are exhausted. Payment state comes from the status API, not delivery success.

An approved redelivery keeps the same event ID for deduplication. Do not generate a second capture to cause a fresh notification.

## Runbook: reconciliation mismatch

Compare provider operation ID, merchant, operation type, currency, amount, and batch version. Separate missing capture, missing refund, duplicate row, and amount difference. Assign the financial discrepancy to Ravi and transport/job failure to Omar.

MockBridge's report is expected at 02:00 UTC; comparison begins at 02:15 UTC. Escalate a missing report at 02:30 UTC. These are simulated schedules. Preserve both evidence sets and do not patch balances manually.

## Runbook: database or provider unavailable

If PostgreSQL cannot durably accept operations, stop accepting new money work and expose readiness failure. If MockBridge fails before dispatch, a controlled retry with the same request identity may be safe. After uncertain dispatch, preserve pending state and reconcile.

## Recovery completion

Recovery is complete when the affected path is verified, unresolved operations have explicit owners, duplicates/invariant violations are excluded, and Maya records the communication/update. Attach sanitized traces, root cause, recovery steps, and prevention action to the incident ticket.
