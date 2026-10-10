# HarborPay Gateway: team roles and ownership

Audience: QA, developers, business analysts, and managers. Purpose: know who owns decisions and where to ask for help.

All contacts, channels, assignments, and policies are fictional training data. Email addresses use the reserved `harborpay.example` domain and are not real support destinations.

## Project contacts

| Role | Fictional contact | Responsibility |
|---|---|---|
| Product Owner | Anika Rao, anika@harborpay.example | Business priorities, payment-rule approval, product acceptance |
| Technical Lead | Dev Mehta, dev@harborpay.example | Architecture, API (application programming interface) contracts, code ownership |
| QA Lead | Priya Sen, priya@harborpay.example | Test strategy, defect triage, quality signoff |
| BA Lead | Kabir Shah, kabir@harborpay.example | Requirements, glossary, acceptance-criteria quality |
| Delivery Manager | Maya Das, maya@harborpay.example | Dependencies, risks, delivery readiness, go/no-go record |
| Platform Lead | Omar Khan, omar@harborpay.example | Environments, deployment, operational recovery |
| Security Lead | Leena Roy, leena@harborpay.example | Access-risk approval, data protection, security incidents |
| Finance/Reconciliation Lead | Ravi Iyer, ravi@harborpay.example | Settlement-report comparison and financial mismatch decisions |

## What each joining role owns

A developer owns implementation and technical tests, not unilateral changes to business rules. A QA engineer owns repeatable tests and clear evidence, not the final business-policy decision. A BA turns stakeholder needs into testable rules and obtains Product Owner approval. A manager coordinates decisions, blockers, and readiness; management approval never substitutes for a required technical or security review.

Every joiner has a named buddy assigned by Maya in the onboarding ticket. The buddy helps locate evidence and routes questions to the correct owner. The buddy cannot approve their own access request.

## Approval matrix

| Decision | Prepares | Required decision or signoff |
|---|---|---|
| Payment/refund business rule | BA with Finance input | Anika; Ravi reviews financial reconciliation effects |
| API or database contract | Developer | Dev; affected consumers and QA review impact |
| Pull request | Developer | Two approvals: relevant code owner and an independent reviewer |
| Test plan and quality evidence | QA | Priya |
| Standard sandbox tool access | Joiner | Line manager approval; Omar provisions |
| Privileged or production access | Joiner with justification | Line manager and Leena; Omar provisions time-limited access |
| Production release | Release owner | Priya quality signoff, Anika business signoff, Omar operational signoff; Maya records go/no-go |
| Reconciliation adjustment | Finance analyst | Ravi; never an ad hoc database edit by a developer |

## Communication and escalation

Use fictional channel `#hpg-onboarding` for joiner questions, `#hpg-engineering` for technical discussion, `#hpg-quality` for test/defect questions, and `#hpg-incidents` for incidents. Track work in project key `HPG` in the issue tracker.

For blocked onboarding, add the missing permission, role, environment, and error summary to the access ticket; contact Omar and your buddy. For unclear requirements, contact Kabir, who obtains Anika's decision. For possible data exposure, contact Leena immediately through the incident process; do not paste sensitive material into chat.

If owners disagree, Maya records the decision needed and coordinates resolution. Until a rule is approved, mark it unresolved rather than treating a guess as project policy.
