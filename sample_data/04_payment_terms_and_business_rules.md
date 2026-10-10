# HarborPay Gateway: payment terms and business rules

Audience: all roles. Purpose: provide the authoritative vocabulary and financial rules.

All amounts, limits, and provider behavior are fictional training data and project-specific sandbox assumptions, not banking advice or industry-wide guarantees.

## Basic payment vocabulary

- A **merchant** sells goods; a **customer** buys them.
- A **payment gateway** passes payment requests between a merchant and a processor.
- **Authorization** asks the provider to approve/reserve the amount. It does not settle funds into the merchant account.
- **Capture** asks the provider to collect an authorized amount.
- **Void** cancels an unused authorization. It is not a refund.
- **Refund** returns some or all of a successfully captured amount.
- **Settlement** is the provider's later reporting and transfer process. MockBridge simulates a report, not a real bank transfer.
- **Reconciliation** compares HarborPay's records with the provider's records and investigates differences.
- A **chargeback/dispute** is a separate customer/bank challenge. HarborPay only records and escalates it in this example.
- **Idempotency** means repeating the same logical request does not create an additional operation. Rules are in the [data guide](10_data_model_and_idempotency.md).

## Currency and amount limits

HarborPay supports INR only. Store money as integer paise; 100 paise equals INR 1.00. The valid payment amount is 100 through 10000000 paise inclusive, equivalent to INR 1.00 through INR 100000.00. Decimal major-unit API amounts, zero, negative amounts, and other currencies are rejected.

Refund amounts are positive integer paise and cannot exceed available refundable value. There is no separate INR 1.00 minimum for refunds; a one-paise refund is allowed when sufficient value remains. Cross-currency refunds and foreign exchange are out of scope.

## Authorization and capture rules

A payment uses manual capture, once, for the full authorized amount. Partial capture, multiple captures, and automatic capture are not supported. A definitive capture failure returns the payment to `AUTHORIZED`; an unresolved capture remains `CAPTURE_PENDING` and blocks another capture.

In the MockBridge sandbox, an unused authorization expires 30 minutes after provider-confirmed authorization. Do not mark it expired while a capture or void outcome is unresolved; resolve that operation first. Void is allowed only before successful capture.

## Refund invariant

For a captured payment:

`available_refund_paise = captured_amount_paise - succeeded_refund_paise - pending_refund_paise`

Successful refunds plus pending reservations must never exceed the captured amount. Reserve the requested amount atomically before contacting MockBridge. A definitive refund failure releases its reservation. An unknown outcome keeps the reservation until resolved.

Example: a 25000-paise capture with 5000 paise successfully refunded and 7000 paise pending has 13000 paise available. A 14000-paise request must be rejected.

## Payment-state boundaries

Payment states are `CREATED`, `AUTH_PENDING`, `AUTHORIZED`, `DECLINED`, `CAPTURE_PENDING`, `CAPTURED`, `VOID_PENDING`, `VOIDED`, and `EXPIRED`. Refunds have separate `PENDING`, `SUCCEEDED`, or `FAILED` states. A fully refunded payment remains `CAPTURED`; its refund totals show that no refundable value remains.

Only a verified provider outcome changes a money-operation result. A timeout does not prove failure. The Product Owner approves changes to these rules with Finance review; developers must not relax them just to pass a test.
