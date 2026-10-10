# HarborPay Gateway: architecture and service boundaries

Audience: developers, QA, BAs, and managers. Purpose: understand components and identify where failures occur.

All services and integrations are fictional training data. This RAG repository does not contain their implementation.

## Main components

| Component | Responsibility | Not responsible for |
|---|---|---|
| Merchant Portal | React/TypeScript user interface for payment search and permitted actions | Storing secrets or deciding final provider outcomes |
| Payment API | Java/Spring Boot application enforcing ownership, state, amounts, and idempotency | Direct collection of raw card details |
| Provider Adapter | Module inside Payment API translating MockBridge requests, status, and callbacks | Bypassing domain validation |
| PostgreSQL | Durable payments, operations, refunds, audit, event inbox/outbox, idempotency | A disposable cache |
| Redis | Short-lived status/read cache and nonauthoritative performance aids | Sole storage of refund reservations or idempotency |
| Background Worker | Payment API worker module processing durable event/outbox and reconciliation jobs | Inventing a financial outcome after timeout |
| MockBridge | Simulated hosted checkout, authorization/capture/refund outcomes, reports | Real bank/card-network processing |

The example uses one backend application with modules and worker execution, not a separate microservice for every step.

## Request path

Merchant Portal -> merchant backend/session -> Payment API -> validated domain operation -> Provider Adapter -> MockBridge.

Before sending a money operation, Payment API records its operation ID, request identity, and pending state in PostgreSQL. A confirmed response updates domain state and writes audit/outbox evidence in a transaction. Unknown outcomes remain pending.

## Asynchronous event path

MockBridge callback -> authenticated webhook endpoint -> durable inbox -> worker -> validated state transition -> durable outbox -> merchant endpoint.

An inbox stores received events before processing. An outbox stores notifications alongside the business change so notification intent is not lost if a process crashes. Notifications can repeat; receivers must deduplicate. Neither pattern claims exactly-once delivery across the network.

## Trust boundaries

The browser is untrusted input. Authenticate callers, check merchant ownership for every payment/refund, and check operation permissions on the server. MockBridge callbacks are external input; verify authenticity and replay protection before storing them.

Card details stay on a hosted provider page. PostgreSQL stores synthetic tokens and IDs, never real primary account numbers (PANs) or card verification values (CVVs). Logs must not expose tokens or credentials.

## Failure boundaries

- Provider unavailable before an operation is dispatched: return a clear retryable error only when no operation was submitted.
- Provider outcome unknown after dispatch: leave pending and reconcile with its operation ID.
- Redis unavailable: durable correctness remains in PostgreSQL; reads may be slower.
- PostgreSQL unavailable: do not accept a money operation that cannot be durably recorded.
- Merchant endpoint unavailable: retain the outbox event and follow bounded notification retries; payment outcome remains unchanged.

Use [API errors](09_api_contracts_and_error_handling.md), [webhooks](11_webhooks_and_provider_sandbox.md), and [monitoring](18_monitoring_incidents_and_runbooks.md) to investigate the relevant boundary.
