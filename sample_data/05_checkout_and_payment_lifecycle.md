# HarborPay Gateway: checkout and payment lifecycle

Audience: developers, QA, BAs, and managers. Purpose: trace checkout and interpret payment states.

All flows, states, and timing assumptions are fictional training data for the MockBridge sandbox.

## Happy path

1. The merchant backend creates a payment for an order, in integer INR paise. HarborPay assigns a payment ID.
2. The customer enters payment details on MockBridge's hosted page. HarborPay receives an opaque synthetic token, not card numbers.
3. The merchant backend submits that token for authorization.
4. MockBridge confirms authorization; HarborPay records `AUTHORIZED`.
5. An authorized merchant operator requests full capture after the order is ready.
6. MockBridge confirms capture; HarborPay records `CAPTURED` and sends a merchant notification.
7. Finance later reconciles the capture with a simulated settlement report.

The example portal calls the merchant backend, not the provider with a private merchant secret embedded in browser code.

## Authoritative payment transition table

| From | Trigger | To |
|---|---|---|
| `CREATED` | Valid authorization operation accepted | `AUTH_PENDING` |
| `AUTH_PENDING` | Verified provider authorization success | `AUTHORIZED` |
| `AUTH_PENDING` | Verified provider decline | `DECLINED` |
| `AUTH_PENDING` | Verified technical failure with no authorization created | `CREATED` |
| `AUTHORIZED` | Full capture operation accepted before expiry | `CAPTURE_PENDING` |
| `CAPTURE_PENDING` | Verified capture success | `CAPTURED` |
| `CAPTURE_PENDING` | Verified capture failure with authorization still usable | `AUTHORIZED` |
| `AUTHORIZED` | Void operation accepted before expiry | `VOID_PENDING` |
| `VOID_PENDING` | Verified void success | `VOIDED` |
| `VOID_PENDING` | Verified void failure with authorization still usable | `AUTHORIZED` |
| `AUTHORIZED` | Confirmed authorization expiry, no unresolved operation | `EXPIRED` |

If a failed capture/void resolves after the authorization deadline, return to `AUTHORIZED` only long enough to evaluate confirmed expiry before accepting new work. If provider status is not conclusive, leave the operation pending for reconciliation.

`DECLINED`, `VOIDED`, and `EXPIRED` are terminal for this payment. A customer can begin a new payment after a definitive terminal outcome, using a new payment ID. Never create a replacement payment just because the original is pending.

## Unknown outcomes and concurrency

HarborPay persists an operation and pending state before contacting MockBridge. A network timeout can occur after the provider accepted an operation. Keep the pending state and use the provider operation ID for status lookup.

Capture and void cannot both win on one authorization. Serialize their state checks with a database transaction/version check. While `CAPTURE_PENDING` or `VOID_PENDING`, reject a competing money operation with `INVALID_STATE`.

## Portal behavior

Show a pending operation as "Processing - outcome not yet confirmed." Disable conflicting action buttons, but enforce the same rule on the server because browser controls are not authorization or concurrency protection.

Refresh from the status API (application programming interface). Merchant notifications may be delayed or delivered more than once; a notification is not a substitute for the authoritative status.

## Completion check

A joiner should trace a decline, successful capture, void, expired authorization, and unresolved timeout. Explain why `CAPTURED` does not mean settled and why refunds have a separate lifecycle in the [refund guide](06_refunds_settlement_and_reconciliation.md).
