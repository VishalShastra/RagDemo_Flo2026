# HarborPay Gateway: data model and idempotency

Audience: developers, QA, and BAs. Purpose: explain durable records, duplicate prevention, and concurrent financial constraints.

All entities and retention choices are fictional training data, not an implemented schema in this repository.

## Durable entities in PostgreSQL

| Entity | Important fields and relationships |
|---|---|
| Merchant | `merchant_id`, active status, allowed permissions/configuration |
| Payment | `payment_id`, `merchant_id`, `order_id`, `amount_paise`, `currency`, `status`, version, authorization expiry |
| Operation | `operation_id`, payment/refund reference, type, provider operation ID, dispatch state, outcome |
| Refund | `refund_id`, `payment_id`, `amount_paise`, `status`, reason, operation reference |
| IdempotencyRecord | Merchant, operation scope, key, normalized request hash, resource/operation IDs, initial response, creation/expiry |
| EventInbox | Provider, event ID, verified event summary, received time, processing outcome |
| EventOutbox | Merchant event ID, resource reference, destination reference, attempt count, next attempt, delivery state |
| AuditEvent | Actor, action, object ID, timestamp, before/after state summary, trace ID |
| ReconciliationResult | Batch/row reference, operation ID, match result, assigned owner |

Use integer paise for amounts, not floating-point rupees. Payment and refund ownership follows the merchant relationship. Redis may cache status but must not decide whether a refund is affordable.

Enforce merchant/order attempt constraints transactionally as well as idempotency. Different request keys racing to create a payable attempt for the same merchant/order must not both succeed. A captured order cannot create another payable attempt even if that payment has been fully refunded; a new sale uses a new order ID.

## Idempotency scope and retention

For accepted mutations, the unique scope is authenticated merchant + operation route including resource ID where applicable + `Idempotency-Key`. A normalized request hash distinguishes payloads. Serialize concurrent attempts at the database unique constraint; do not rely on a Redis lock alone.

Retain accepted records for seven sandbox days. Expiry of a key does not make a duplicate business operation legitimate; state and order constraints still apply. Seven days is a demo assumption, not a production retention recommendation.

## Replay behavior

- Same scoped key and same content: return the stored initial response/resource reference and perform no second provider operation.
- For an initially pending response, replay keeps that initial response; use the supplied status URL to learn the current outcome.
- Same scoped key and different content: HTTP 409 `IDEMPOTENCY_CONFLICT`; do not dispatch.
- New key while an operation is unresolved: lifecycle/concurrency checks reject conflicting work. A new key is not a timeout recovery technique.
- Invalid requests rejected before acceptance do not create an accepted operation; corrected requests still undergo all validation.

Separate the client idempotency key from the provider operation ID. Record a stable provider identity before dispatch, and reuse it only under MockBridge's documented deduplication contract.

## Atomicity and refund reservations

Within one database transaction, validate resource state, reserve available refund value, create the operation/refund, and bind its idempotency record. After a verified outcome, update state/totals and audit/outbox records atomically.

For a 25000-paise capture with 5000 succeeded and 7000 pending refunds, only 13000 is available. Two concurrent 10000-paise requests cannot both reserve successfully. Database serialization/version checks must reject the loser with `REFUND_LIMIT_EXCEEDED`; neither a portal balance display nor cache is sufficient.

## Crash recovery and migration

A crash after provider acceptance can leave a pending durable operation. Recovery looks up its provider operation ID and processes verified results. Do not remove the pending record to unblock a user.

Use versioned database migrations and backward-compatible changes. Preserve historical audit and financial records. Application rollback does not reverse payments; [deployment guidance](17_ci_cd_deployment_and_rollback.md) explains the boundary.
