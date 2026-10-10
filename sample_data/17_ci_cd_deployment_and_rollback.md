# HarborPay Gateway: CI/CD, deployment, and rollback

Audience: developers, QA, Platform, and managers. Purpose: describe release gates and safe recovery.

All pipelines, windows, and approvals are fictional training data. No deployment infrastructure is included in this repository.

CI/CD means continuous integration and continuous delivery: automatically verify changes, build a versioned artifact, and promote it through approved environments.

## Pull-request and build gates

Each pull request needs two approvals: a relevant code owner and an independent reviewer. The author cannot satisfy either approval. Required checks are compile/type-check, code style, unit tests, API contract tests, integration tests, dependency checks, secret scanning, and migration validation.

Payment-rule changes require Product Owner approval before merge. Security-impacting changes require Leena's review. A passing pipeline does not replace these decisions.

Build an immutable backend/portal artifact with a version and source commit reference. Promote the same tested artifact to later environments; do not rebuild unreviewed code during promotion.

## Environment promotion

1. Local: developer tests with isolated synthetic fixtures.
2. Sandbox: shared integration, MockBridge behavior, idempotency, webhook, and negative tests.
3. UAT (user acceptance testing): approved business scenarios reviewed by Anika with BA support.
4. Hypothetical production: only after release signoffs and operational readiness.

Priya signs quality evidence, Anika signs business acceptance, and Omar signs operational readiness. Maya records the final go/no-go and unresolved risks. A manager cannot waive a failing financial invariant.

## Deployment checklist

- Verify artifact/version, environment, secret references, and compatible database schema.
- Confirm migrations are reviewed and the previous application remains compatible during rollout.
- Identify release owner, rollback artifact, monitoring dashboards, and incident contact.
- Confirm no unresolved critical/high release-blocking defects or financial mismatches.
- Deploy in the fictional normal window: Tuesday or Thursday, 10:00-12:00 UTC.
- Validate readiness, synthetic approved payment flow, refund limits, status reads, and notifications.
- Observe pending-operation backlog and error rates; record outcome and approvals.

Emergency changes outside the normal window need Priya, Anika, and Omar's signoffs; Maya records the exception and Leena reviews security implications. Emergency status does not authorize an unreviewed money correction.

## Rollback boundaries

If the application regresses, Omar can halt rollout and restore the previously approved compatible artifact. Check whether the schema supports it first. Prefer backward-compatible expand/contract migrations; a destructive schema reversal is not a routine rollback.

Rolling back software does not reverse a capture, refund, or settlement report. Preserve pending operations, idempotency records, inbox/outbox events, and audit evidence. Reconcile operations accepted during the incident before resuming writes.

Disable an affected money-operation path if necessary instead of retrying blindly. Financial corrections go through Ravi's audited decision process. Do not restore an old database snapshot over newer money-operation records.

## Evidence to attach

Attach build version, commit, test results, business acceptance, signoffs, migration assessment, verification traces, and release decision. Exclude secrets and raw customer/provider payloads. The [manager guide](15_manager_delivery_and_release_governance.md) defines readiness ownership.
