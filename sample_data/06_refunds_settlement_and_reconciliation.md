# HarborPay Gateway: refunds, settlement, and reconciliation

Audience: QA, BAs, developers, managers, and Finance. Purpose: understand post-capture operations and exception ownership.

All financial examples, report schedules, and provider outcomes are fictional training data. No real money moves.

## Full and partial refunds

Only a `CAPTURED` payment can have a refund. A permitted merchant operator supplies positive integer `amount_paise` and a reason. HarborPay checks ownership, permission, and available refundable value, then reserves the amount in a database transaction.

A full refund requests all currently available value. A partial refund requests less. Multiple refunds are allowed, but succeeded refunds plus pending reservations must not exceed the captured amount. A rejected over-limit request must not contact MockBridge.

For a 25000-paise capture, a successful 5000-paise refund leaves 20000 paise refundable if no other refund is pending. A second 20000-paise refund can complete the full return. The payment remains `CAPTURED`; the refund records and totals describe the returned amount.

## Refund state and failure handling

| From | Evidence | To | Reservation |
|---|---|---|---|
| New accepted refund | Valid request stored before provider call | `PENDING` | Reserve amount |
| `PENDING` | Verified refund success | `SUCCEEDED` | Convert reservation into successful refunded total |
| `PENDING` | Verified refund failure, no return made | `FAILED` | Release amount |
| `PENDING` | Timeout, delayed callback, or unclear provider status | `PENDING` | Keep amount reserved |

Do not automatically fail a pending refund just because a timer elapsed. Platform checks provider status; Finance investigates unresolved financial differences. A new refund after definitive failure is a new business operation, not a replay of the old idempotency key.

## Settlement-report assumptions

MockBridge publishes one simulated daily batch at 02:00 UTC (Coordinated Universal Time), covering confirmed captures and succeeded refunds from the prior UTC day. Authorization and pending refunds are not settlement rows. This simplified report has no fees or real bank transfer; it is not a production settlement promise.

Each report has a batch ID, row ID, merchant ID, provider operation ID, operation type, currency, and integer amount in paise. Reconcile gross captures and refunds separately; a matching net total alone can hide errors.

## Reconciliation workflow

At 02:15 UTC, the reconciliation job compares immutable provider report rows with HarborPay's confirmed operation records. Match operation ID, merchant, type, currency, and amount; record matched, missing, duplicate, or different-amount results.

Do not create a refund or capture to "balance" a report. Preserve evidence and route discrepancies to Ravi. Omar investigates missing delivery or job failures. If the report is absent at 02:30 UTC, alert Omar and Ravi. A corrected report requires a new version linked to the previous batch; do not overwrite audit evidence.

## Disputes and adjustments

A dispute is not a normal merchant refund. Record the dispute reference, affected payment, and evidence request; route it to Ravi and Anika. Automated dispute decisions and chargeback debits are out of scope.

Manual financial adjustments require Finance approval and an audited workflow. Developers and managers must not edit balances directly in the database. See [incident runbooks](18_monitoring_incidents_and_runbooks.md) for unsafe or unresolved outcomes.
