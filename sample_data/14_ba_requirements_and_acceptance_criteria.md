# HarborPay Gateway: BA requirements and acceptance criteria

Audience: joining business analysts (BAs). Purpose: translate payment needs into clear, approved, testable requirements.

All stories, stakeholders, and examples are fictional training data.

## BA prerequisites and learning path

Obtain requirements-wiki, issue-tracker, and read-only sandbox access. Read the [business rules](04_payment_terms_and_business_rules.md), [lifecycle](05_checkout_and_payment_lifecycle.md), [refunds/reconciliation](06_refunds_settlement_and_reconciliation.md), and [API contracts](09_api_contracts_and_error_handling.md).

Kabir owns BA onboarding. Anika approves product policy; Ravi reviews financial effects; Priya reviews testability; Dev reviews feasibility and contracts. A BA records unresolved assumptions rather than deciding them silently.

## Questions to clarify before a story is Ready

- Which actor and merchant role performs the action?
- What state allows it, and what states prohibit it?
- What currency, amount unit, limit, and reservation rules apply?
- What happens on duplicate, timeout, decline, and conflicting operation?
- What evidence confirms success, and what remains pending?
- What does the customer/operator see, and who handles exceptions?
- Does the change alter reporting, reconciliation, permissions, or audit?

Separate product rules from UI (user interface) wording and implementation choices. "Refund quickly" is not an acceptance criterion; specify permitted amount, state, outcome, and measurable evidence.

## First BA task: partial refund story

Illustrative `HPG-203`:

> As a Merchant Supervisor, I want to request a partial refund of a captured payment so that I can return the amount of a cancelled item without returning the whole order.

Acceptance criteria:

1. **Given** a captured 25000-paise payment owned by the merchant and no existing refunds, **when** an authorized supervisor requests 5000 paise, **then** one refund is created and reserved before provider dispatch.
2. **Given** 5000 paise succeeded and 7000 paise pending, **when** 14000 paise is requested, **then** reject with `REFUND_LIMIT_EXCEEDED`; no provider call occurs.
3. **Given** an accepted request and the same scoped idempotency key/body, **when** the request repeats, **then** return its initial response/resource without another refund.
4. **Given** a provider timeout, **when** the outcome is unknown, **then** show pending status and keep the reservation.
5. **Given** an operator lacking refund permission, **when** they submit the action directly, **then** return `FORBIDDEN`, even if they bypass the portal.

Ask Anika to approve the story with Ravi's financial review. Priya maps each criterion to tests; Dev checks API/schema impact.

## Traceability and change control

Link business-rule section -> story -> acceptance criterion -> test case -> defect/release evidence. Store the decision owner and rationale. A change to currency support, refund limits, or capture behavior requires a new approved decision and corresponding tests/contracts.

Do not copy a rule into several documents with different values. Point to the authoritative business-rule source. If stakeholders disagree, mark the story not Ready and ask Maya to coordinate a decision.

## BA completion evidence

Attach the approved story, glossary clarification, stakeholder decision log, test mapping, and reviewed walkthrough to the onboarding ticket. Kabir accepts BA readiness when another person can derive the expected result without guessing.

Escalate policy ambiguity to Kabir/Anika, financial questions to Ravi, and feasibility questions to Dev. Read-only BA access does not permit issuing real or simulated refunds outside an approved exercise.
