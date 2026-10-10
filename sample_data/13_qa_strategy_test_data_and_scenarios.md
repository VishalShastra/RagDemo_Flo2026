# HarborPay Gateway: QA strategy, test data, and scenarios

Audience: joining QA (quality assurance) engineers. Purpose: learn the system and produce repeatable payment-quality evidence.

All tests, fixtures, amounts, and defects are fictional training data. Use synthetic inputs only.

## QA prerequisites and learning path

Obtain test-repository, sandbox, issue-tracker, and synthetic-log access. Read [business rules](04_payment_terms_and_business_rules.md), [lifecycle](05_checkout_and_payment_lifecycle.md), [refunds](06_refunds_settlement_and_reconciliation.md), [API errors](09_api_contracts_and_error_handling.md), and [MockBridge fixtures](11_webhooks_and_provider_sandbox.md).

Priya owns QA onboarding and accepts evidence. Omar handles environment access; Dev investigates code failures. A shared sandbox failure must be distinguished from a product defect before changing expected results.

## Test layers and tooling examples

The fictional backend uses JUnit and integration tests with isolated PostgreSQL/Redis fixtures. Contract tests verify schemas and status/error semantics. Portal tests use component tests and Playwright browser scenarios. These tool names describe the fictional project; they are not additional Langflow dependencies.

Use API (application programming interface) tests to verify server permissions even when browser buttons are hidden. MockBridge supports deterministic declines, delayed outcomes, failures, duplicates, and reordered events.

## Synthetic baseline fixture

Use merchant `demo_merchant_alpha` and order `demo_order_001` for an isolated 25000-paise INR payment. Use `demo_token_approved` or `demo_token_declined` for authorization. Use a second merchant `demo_merchant_beta` for cross-merchant isolation tests.

Do not reuse a shared order/key accidentally between independent tests. Replays deliberately use the same scoped key. Reset only your dedicated local test fixtures or assigned sandbox merchant through the approved harness.

## Minimum scenario matrix

| Scenario | Expected evidence |
|---|---|
| Valid create/authorize/full capture | `CREATED -> AUTH_PENDING -> AUTHORIZED -> CAPTURE_PENDING -> CAPTURED`; one capture operation |
| Declined authorization | `DECLINED`; capture rejected; no successful collection |
| Payment amounts 99, 100, 10000000, 10000001 paise | First/last rejected, inclusive valid boundaries accepted |
| Zero/negative/fractional amount or non-INR currency | `INVALID_REQUEST`; no provider operation |
| Partial/multiple capture attempt | Unsupported input/state rejected, no additional capture |
| Same idempotency key and same body | Initial response/resource replayed; only one provider operation |
| Same scoped key with changed amount | `IDEMPOTENCY_CONFLICT` |
| Capture timeout after provider accepts | `CAPTURE_PENDING`, then verified resolution; no new capture/key |
| Capture/void race | One legal operation wins; other rejected with `INVALID_STATE` |
| Concurrent refunds exceeding available value | At most affordable reservations accepted; invariant preserved |
| Failed refund | `FAILED`; reserved amount released only after definitive failure |
| Unknown refund | `PENDING`; reservation retained |
| Duplicate/out-of-order provider event | No doubled totals and no state regression |
| Invalid signature or stale delivery timestamp | Webhook rejected; no business update |
| Cross-merchant lookup or forbidden refund | Nonrevealing `NOT_FOUND` or permission `FORBIDDEN`, respectively |
| Merchant notification retries exhausted | Failed-delivery evidence; captured payment unchanged |
| Reconciliation amount difference | Mismatch assigned to Finance; no automatic balance patch |

## First QA task

Illustrative `HPG-202`: verify partial-refund reservation logic. Capture 25000 paise, complete a 5000-paise refund, and hold a 7000-paise refund pending. Verify 13000 remains available and a new 14000-paise refund is rejected with `REFUND_LIMIT_EXCEEDED` before provider dispatch.

Resolve the pending 7000-paise refund as definitively failed using the mock scenario. Verify available value returns to 20000 paise. Repeat the duplicate/concurrent request cases and record operation counts.

## Defect reporting and completion

A defect contains environment, build, scenario, sanitized IDs, steps, expected result with source rule, actual result, impact, and repeatability. Include server/operation evidence, not only a screenshot.

Priya prioritizes with Dev and Anika. Attach a test run, coverage of positive/negative/concurrent outcomes, a sample defect, and first-task review to the onboarding ticket. QA readiness means you can explain why a test is correct and reproduce it.
