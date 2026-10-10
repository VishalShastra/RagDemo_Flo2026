# HarborPay Gateway: manager delivery and release governance

Audience: joining project/delivery managers and team managers. Purpose: coordinate onboarding, dependencies, risk, and release decisions.

All delivery practices, schedules, and examples are fictional training data.

## Manager prerequisites and learning path

Obtain delivery-board, requirements-wiki, and read-only report access. Read [ownership](02_team_roles_and_ownership.md), [lifecycle](05_checkout_and_payment_lifecycle.md), [architecture](07_architecture_and_service_boundaries.md), [security](16_security_privacy_and_access_controls.md), [deployment](17_ci_cd_deployment_and_rollback.md), and [incident runbooks](18_monitoring_incidents_and_runbooks.md).

Maya owns manager onboarding. Managers coordinate decisions and record readiness; they do not bypass technical, financial, security, or QA (quality assurance) controls.

## Delivery cadence

The fictional team uses a daily blocker check, weekly planning/refinement, and a review/demo at the end of each delivery iteration. The cadence is a coordination convention, not a production-release entitlement.

Work moves `Ready -> In Progress -> In Review -> In Test -> Done`. Ready requires agreed scope, acceptance criteria, owner, and dependencies. Done requires accepted criteria, appropriate review, passing tests, documentation, and no unowned release-blocking defect.

## Dependency and risk register

Record the risk/dependency, affected outcome, owner, evidence, mitigation, decision needed, and next review trigger. Typical dependencies include provider sandbox availability, test merchant access, API contract agreement, migration compatibility, and settlement-report fixtures.

Escalate access blockers to Omar, business ambiguity to Kabir/Anika, quality gaps to Priya, financial mismatches to Ravi, and security concerns to Leena. Track ownership rather than reporting "the team is investigating" indefinitely.

## First manager task

Illustrative `HPG-204`: prepare readiness for a partial-refund feature.

1. Identify BA approval, API/state changes, refund concurrency tests, and financial-report impact.
2. Record sandbox/fixture dependencies with named owners.
3. Build a release-readiness checklist with evidence links and remaining risks.
4. Run a review with Priya, Anika, and Omar; obtain the required signoffs or record a no-go.
5. Identify rollback limitations and the incident contact.

Attach the register, reviewed checklist, and decision record to the onboarding ticket. Maya accepts manager readiness when every blocker has an owner and the go/no-go is justified by evidence.

## Release readiness and signoffs

Priya signs quality, Anika signs business acceptance, and Omar signs operational readiness. Maya records the final go/no-go. Leena reviews security implications and Ravi reviews affected financial rules/reporting.

Required evidence includes tested artifact/version, accepted stories, passing financial-invariant tests, reviewed migrations, secret/configuration readiness, monitoring, support ownership, and compatible rollback. Do not approve release with an unresolved critical/high release-blocking defect or financial mismatch.

Normal releases use Tuesday/Thursday 10:00-12:00 UTC (Coordinated Universal Time). The deployment guide owns that schedule and emergency-exception process.

## Reporting and stakeholder communication

Report completed outcomes, blocked decisions, test evidence, unresolved operation/mismatch risks, and next action owners. Avoid treating number of closed tickets as proof of payment correctness.

During incidents, Maya provides stakeholder updates from the incident coordinator's verified facts. Do not promise a refund/capture succeeded until the provider outcome is confirmed. Application rollback cannot reverse money already processed.
