# HarborPay Gateway: developer workflow and code review

Audience: joining backend and portal developers. Purpose: deliver a first safe change and understand engineering expectations.

All repositories, tickets, workflows, and examples are fictional training data; payment source code is not included here.

## Developer prerequisites and learning path

Obtain approved code, issue-tracker, design, and sandbox permissions. Understand integer paise, manual capture, pending outcomes, and refund reservations before changing payment logic.

Read the [architecture](07_architecture_and_service_boundaries.md), [setup](08_repositories_local_setup_and_environments.md), [API contracts](09_api_contracts_and_error_handling.md), [data model](10_data_model_and_idempotency.md), and [webhooks](11_webhooks_and_provider_sandbox.md). Trace one request from portal through domain validation to MockBridge and back to durable state.

Dev is the developer onboarding owner. Omar handles environment access; Priya helps with test scenarios. Your buddy reviews navigation and setup but does not replace required code reviews.

## First developer task

Illustrative ticket `HPG-201`: add a portal explanation for `CAPTURE_PENDING` and disable the conflicting void button while capture is unresolved.

1. Confirm the accepted message with Kabir: "Processing - outcome not yet confirmed."
2. Identify the status response and portal component; do not create a new payment state.
3. Implement the display and button behavior with component tests.
4. Add a test that direct server requests still reject void during pending capture.
5. Show that `CAPTURED` and `AUTHORIZED` displays remain unchanged.
6. Submit a pull request with screenshots using synthetic IDs, test output, and a link to the lifecycle rule.

This is a user-experience improvement, not a replacement for server-side state checks.

## Daily change workflow

Move the issue through `Ready -> In Progress -> In Review -> In Test -> Done`. A ticket is Ready only when scope, acceptance criteria, owner, and dependencies are clear.

Create branch `HPG-<number>-<short-description>`. Keep one coherent change per pull request. Update directly related contracts and tests in the fictional payment project when behavior changes.

Use the project's build wrappers and lockfiles. Run targeted unit/component tests first, then the relevant integration/contract checks. Do not add a dependency simply to avoid understanding existing code.

## Code-review checklist

- Does the change enforce merchant ownership and the right operation permission?
- Are amounts integer paise and state transitions legal?
- Can retries or concurrent requests cause duplicate captures/refunds?
- Are pending refunds reserved durably, including after crashes?
- Are idempotency and provider operation identities preserved?
- Are errors explicit and logs sanitized?
- Are contract/schema changes backward-compatible and tests meaningful?

Every pull request needs two approvals: a relevant code owner and an independent reviewer, neither the author. Changes to payment rules require Anika's approval with Finance review; security-impacting changes require Leena.

## Developer completion evidence

Attach the approved pull request, passing relevant tests, contract/state reasoning, and safe demonstration to the onboarding ticket. Dev accepts technical completion; the line manager records overall onboarding.

Blocked setup goes to Omar. Ambiguous rule/acceptance criteria go to Kabir and Anika. A possible money-invariant violation goes to Dev, Priya, and Ravi, not a silent workaround.

## Safe debugging

Use synthetic fixtures and trace IDs. Do not paste tokens or credentials into issues. Do not delete pending operations, bypass refund caps, or edit production balances. Use the [incident runbooks](18_monitoring_incidents_and_runbooks.md) for unclear outcomes.
