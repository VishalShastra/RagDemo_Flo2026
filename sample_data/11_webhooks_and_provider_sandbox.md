# HarborPay Gateway: webhooks and provider sandbox

Audience: developers and QA; BAs use the behavior examples. Purpose: test asynchronous outcomes safely.

All tokens, events, signatures, retry schedules, and MockBridge behavior are fictional training data. Tokens below are symbolic fixture labels, not real payment tokens or card numbers.

## Synthetic provider scenarios

| Fixture label | MockBridge behavior | Expected HarborPay handling |
|---|---|---|
| `demo_token_approved` | Authorization succeeds | `AUTHORIZED`; eligible for full manual capture |
| `demo_token_declined` | Authorization is definitively declined | `DECLINED`; no capture |
| `demo_token_auth_delayed` | Authorization response times out; verified success arrives later | Keep `AUTH_PENDING`, then `AUTHORIZED` |
| `demo_capture_delayed` | Scenario setting: capture accepted, response lost | Keep `CAPTURE_PENDING`; lookup confirms `CAPTURED` |
| `demo_refund_failed` | Scenario setting: definitive refund failure | Refund `FAILED`; release reservation |
| `demo_refund_unknown` | Scenario setting: refund outcome unresolved | Refund `PENDING`; reservation retained |

Authorization fixture labels are supplied as `payment_token`. Capture/refund scenario labels configure the mock fixture; they are not extra API body fields. Test harness resets use isolated local fixtures or a dedicated sandbox merchant, never shared/production records.

## MockBridge operation identity

MockBridge's fictional contract deduplicates a stable provider operation ID within the same merchant and operation type. Repeating that identity with the same content returns the current operation outcome and does not perform the financial action again. Reusing it with different content is rejected.

HarborPay persists the provider operation ID before dispatch. Recovery first looks up that ID; a resend is allowed only under this mock deduplication contract and never under a newly generated identity. Provider status lookup can remain unresolved, in which case the HarborPay operation stays pending. Real integrations require their own reviewed provider contract.

## Incoming provider webhook

The illustrative endpoint is `POST /v1/webhooks/mockbridge`. MockBridge sends a stable `event_id`, `provider_operation_id`, event type, resource outcome, amount, currency, and timestamp. Treat even authentic events as input requiring business validation.

The example signature uses HMAC-SHA256 (keyed hash message authentication code with SHA-256) over the timestamp and exact raw body. Verify the signature in constant time, with a five-minute timestamp freshness window. Obtain keys from approved secret storage; no keys are included here. Each delivery attempt has a fresh delivery timestamp/signature while retaining its original event ID.

Reject invalid signatures with HTTP 401. Reject malformed authenticated payloads with HTTP 400. Return HTTP 200 only after the verified event or its duplicate receipt is durably stored. A storage failure returns HTTP 503 so the sender can retry. Acknowledge storage, not an invented business success.

## Duplicates and event ordering

Uniquely record provider + `event_id` in PostgreSQL. Receiving the same event twice may return HTTP 200 but must not update money totals twice.

Check operation identity, merchant, amount, currency, and legal state transition before applying an event. An event that contradicts terminal state is quarantined for investigation. A delayed authorization event must not regress a captured payment. For conflicting/out-of-order evidence, look up current provider operation status rather than applying arrival order as truth.

## Outgoing merchant notifications

HarborPay signs outbound notifications using a merchant-specific secret reference. Apply the same timestamp/signature convention; no secret appears in the payload. Merchant receivers deduplicate by HarborPay event ID and use the status API for current state.

Send an initial attempt, then at most three retries after 1, 5, and 15 minutes from the preceding failed attempt. HTTP 2xx acknowledges delivery; non-2xx or transport timeout triggers the next bounded attempt. After exhaustion, put the event in the failed-delivery queue, alert Omar, and retain evidence. Retry timing affects notifications, not the payment's financial outcome.

## Completion check

QA proves that duplicate events do not double-count, out-of-order events do not regress state, invalid signatures are rejected, and failed notification delivery does not undo capture. Developers inspect inbox/outbox evidence; logs contain IDs and sanitized summaries, not raw signed bodies or tokens.
