# HarborPay Gateway: Jira known issues and troubleshooting

Audience: all joining roles. Purpose: search concrete symptoms and find safe actions.

All `HPG-*` tickets below are fictional training data simulating an issue-tracker export. They are not real Jira records. Status describes the fictional ticket, not a guarantee that your environment has the fix.

## HPG-101: sandbox portal returns Forbidden

- Status: Resolved.
- Symptom: a new QA/BA/manager account can sign in but cannot view the sandbox merchant.
- Root cause: approved account lacks its sandbox group/merchant assignment.
- Resolution: attach the requested role and sandbox merchant to the access ticket; Omar provisions after line manager approval.
- Verify: permitted read works; refund remains denied for a read-only role.
- Escalation: Omar and the buddy through `#hpg-onboarding`; do not borrow another person's login.

## HPG-102: repeated create request makes a duplicate attempt

- Status: Resolved.
- Symptom: a client sends a new idempotency key after losing the first response.
- Root cause: client generates a key per HTTP attempt rather than per logical request.
- Resolution: reuse the same scoped key/body and inspect the returned payment ID/status. Server order/state constraints also block a competing unresolved/captured attempt.
- Verify: one accepted payment/operation for the logical request; replay returns the initial response.
- Escalation: Dev; involve Priya for retry tests. Existing suspicious duplicates go to Ravi/Omar for investigation, not deletion.

## HPG-103: capture stays pending after a timeout

- Status: Investigating.
- Symptom: portal shows `CAPTURE_PENDING`; client received no final confirmation.
- Known condition: MockBridge may have accepted capture before the response was lost.
- Action: use the stored provider operation ID for status lookup; keep the pending state until evidence resolves it.
- Verify: one capture, legal transition, audit evidence; no new request key.
- Escalation: Omar and Ravi. The ticket is unresolved; there is no approved "mark failed" workaround.

## HPG-104: duplicate webhook increases refund total twice

- Status: Resolved.
- Root cause: consumer applied repeated events without a durable unique provider/event ID check.
- Resolution: record the verified event in the inbox and apply its business effect once in the transaction.
- Verify: sending the same event twice acknowledges receipt but changes totals once.
- Escalation: Dev/Priya; any actual invariant breach goes to Ravi/Omar as an incident.

## HPG-105: webhook signature rejected after retry

- Status: Resolved.
- Symptom: a replayed delivery is outside the five-minute freshness window.
- Root cause: test sender reused the old delivery timestamp/signature.
- Resolution: generate a fresh signed delivery timestamp for the retry, keep the original event ID, and verify clock alignment and configured secret reference.
- Verify: fresh valid delivery accepted; stale/tampered delivery still rejected.
- Escalation: Omar/Leena; do not disable signature verification.

## HPG-106: refund limit exceeded although portal shows enough

- Status: Expected behavior.
- Symptom: HTTP 409 `REFUND_LIMIT_EXCEEDED` during concurrent/pending refunds.
- Explanation: the portal displayed an older total or ignored pending reservations.
- Action: refresh authoritative status; count succeeded plus pending amounts. For capture 25000, succeeded 5000, pending 7000, only 13000 paise is available.
- Verify: no dispatch for an over-limit request; server-side invariant holds.
- Escalation: Dev for stale display, Ravi for a genuine money discrepancy; never bypass the cap.

## HPG-107: settlement report does not match local records

- Status: Investigating.
- Symptom: a report row has a different amount, missing operation, or duplicate reference.
- Action: preserve batch/version and operation evidence; compare merchant, type, currency, and amount independently.
- Verify: reconciliation assigns a clear mismatch type and owner, not an automatic compensating payment.
- Escalation: Ravi for financial differences; Omar for missing reports/job failures.

## HPG-108: backend not ready after local setup

- Status: Resolved.
- Symptom: readiness reports database/migration failure.
- Root cause: fictional setup used the wrong database configuration or skipped migrations.
- Resolution: check the intended local environment, database connection and migration results; route credentials through approved storage.
- Verify: readiness and an isolated synthetic scenario succeed.
- Escalation: Omar for environment, Dev for migration errors. Do not reset a shared database.

## HPG-109: captured payment has failed merchant notification

- Status: Expected behavior.
- Explanation: merchant delivery failed after the initial attempt and three retries; money state is independent of notification delivery.
- Action: inspect the failed-delivery queue and status API; coordinate approved redelivery with the same event ID.
- Verify: deduplicated merchant receipt; no second capture.
- Escalation: Omar. See the [webhook guide](11_webhooks_and_provider_sandbox.md).
