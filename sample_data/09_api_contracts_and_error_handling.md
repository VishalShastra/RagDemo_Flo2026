# HarborPay Gateway: API contracts and error handling

Audience: developers, QA, and BAs. Purpose: define a consistent example application programming interface (API).

All contracts, IDs, and payloads are fictional training data. These routes are not served by this RAG repository.

## Authentication and request identity

Use transport encryption outside local development. A server-side credential/session identifies the merchant and permissions; never trust a `merchant_id` supplied in a body to establish ownership. Browser code must not contain merchant API secrets.

Every mutation requires `Idempotency-Key`; retain accepted records for seven sandbox days as described in the data guide. The client sends `X-Request-ID` when available; HarborPay creates a trace ID if absent. Neither header replaces authentication.

## Example endpoints

| Operation | Route | Body fields | Required permission |
|---|---|---|---|
| Create | `POST /v1/payments` | `order_id`, `amount_paise`, `currency` | `payment:create` |
| Authorize | `POST /v1/payments/{payment_id}/authorize` | `payment_token` | `payment:authorize` |
| Capture | `POST /v1/payments/{payment_id}/capture` | None; full amount only | `payment:capture` |
| Void | `POST /v1/payments/{payment_id}/void` | `reason` | `payment:void` |
| Refund | `POST /v1/payments/{payment_id}/refunds` | `amount_paise`, `reason` | `payment:refund` |
| Payment status | `GET /v1/payments/{payment_id}` | None | `payment:read` |
| Refund status | `GET /v1/payments/{payment_id}/refunds/{refund_id}` | None | `payment:read` |

Reject unknown mutation fields rather than silently accepting unsupported partial capture. Order IDs are merchant-scoped. A new payment for the same order requires a prior definitive failed/voided/expired attempt; an unresolved or captured attempt blocks another payable attempt.

## Synthetic request and response

Example create body; `demo_order_001` is a training identifier:

```json
{"order_id":"demo_order_001","amount_paise":25000,"currency":"INR"}
```

Create returns HTTP 201 with `payment_id`, `order_id`, `amount_paise`, `currency`, and `status: "CREATED"`. A synchronous confirmed authorization/capture/void returns HTTP 200 with current payment state and `operation_id`. A confirmed decline also returns HTTP 200 with `status: "DECLINED"` and a safe business reason; a decline is not a server crash.

An accepted unresolved money operation returns HTTP 202, `operation_id`, current pending status, and a `status_url`. An accepted refund has `refund_id`; a synchronously completed new refund returns HTTP 201, otherwise HTTP 202 with `status: "PENDING"` and its refund status URL.

Payment status returns HTTP 200 with payment identity, currency, amount, current state, and `captured_amount_paise`, `succeeded_refund_paise`, `pending_refund_paise`, and `available_refund_paise`. Before capture, these financial totals are zero. Include the unresolved operation ID when applicable. Refund status returns its ID, parent payment ID, amount, current refund state, and operation ID.

Available refund value in a read response is informational: a later mutation must recheck the amount atomically because another request may have reserved value meanwhile.

## Stable error taxonomy

| HTTP status | Error code | Meaning and caller action |
|---|---|---|
| 400 | `INVALID_REQUEST` | Missing field, unsupported currency, amount format/limit, or missing idempotency key; correct the request |
| 401 | `UNAUTHENTICATED` | No valid authentication; use approved login/credential process |
| 403 | `FORBIDDEN` | Authenticated caller lacks permission |
| 404 | `NOT_FOUND` | Resource absent or not visible to this merchant; do not reveal another merchant's object |
| 409 | `IDEMPOTENCY_CONFLICT` | Same scoped key with different request content |
| 409 | `INVALID_STATE` | Operation conflicts with lifecycle, pending operation, or unresolved/captured order attempt |
| 409 | `REFUND_LIMIT_EXCEEDED` | Requested refund exceeds currently available value |
| 429 | `RATE_LIMITED` | Respect `Retry-After`; use the same logical request identity |
| 503 | `PROVIDER_UNAVAILABLE` | No provider operation was dispatched; controlled retry may be appropriate |

An error body contains `code`, a safe `message`, and `trace_id`; it never contains secrets or raw provider/card data. An unexpected internal failure is HTTP 500 `INTERNAL_ERROR`; callers look up status before retrying a money operation.

Do not return `PROVIDER_UNAVAILABLE` after an uncertain dispatch. Keep the durable operation pending and return/present its status when possible. A lost response can happen even after commit; use idempotency and status lookup, not a new key.
