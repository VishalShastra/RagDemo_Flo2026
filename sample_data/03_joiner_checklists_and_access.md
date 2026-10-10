# HarborPay Gateway: joiner checklists and access

Audience: all joining roles and their buddies. Purpose: request only necessary access and prove onboarding readiness.

All accounts, requests, permissions, and systems described here are fictional training data.

## Common onboarding sequence

1. Obtain your role, line manager, and buddy from the `HPG` onboarding ticket.
2. Read the overview and payment lifecycle; explain authorization, capture, and refund to your buddy.
3. Complete the project's security briefing and use a managed device.
4. Request named accounts through the fictional Access Desk at `https://access.harborpay.example`.
5. Verify each approved permission yourself and record the result in the onboarding ticket.
6. Complete your role's first task and have the role lead review the evidence.

All tools use single sign-on (SSO) with multi-factor authentication (MFA). Use the approved identity application; SMS verification and shared logins are not accepted in this fictional policy. Credentials are issued by the access process, never by these documents.

## What an access request must contain

Use request type `HarborPay Project Access`. Include name, role, line manager, buddy, environment, requested group, business reason, and requested expiry for privileged access. The line manager approves standard access and Omar provisions it. Production or privileged access also requires Leena's approval and expires after the approved support session.

New joiners do not receive production database access by default. Readiness never requires examining real customer records.

## Minimum role permissions

| Role | Standard sandbox permissions | Not granted by default |
|---|---|---|
| Developer | Code repository, issue tracker, design wiki, sandbox API, synthetic logs | Production writes, provider administration |
| QA engineer | Test repository, issue tracker, sandbox test runner, synthetic fixtures, sandbox observability | Production payment operations |
| BA | Requirements wiki, issue tracker, read-only sandbox portal and sample API documentation | Database writes, merchant refunds |
| Manager | Delivery boards, requirements wiki, read-only reports and sandbox portal | Secret stores, production operations |

Additional access needs a separate justified request. Portal permissions are described in the security guide; job title alone does not authorize merchant actions.

## Readiness checkpoints

- **Knowledge ready:** joiner identifies the merchant, provider, payment state, and owner for a question.
- **Access ready:** approved tools open under the joiner's own account; permission errors are recorded rather than bypassed.
- **Practice ready:** first role task uses synthetic data in local or sandbox environment.
- **Onboarding complete:** role lead accepts the task evidence, security briefing is recorded, and unresolved blockers have owners.

The buddy validates navigation and setup; the line manager records completion. Do not close an onboarding ticket merely because accounts were created.

## Role evidence

Developers attach a reviewed pull request and passing test evidence. QA attaches test runs, sanitized evidence, and a sample defect. BAs attach an approved story with measurable criteria and a traceability link. Managers attach a dependency/risk register and a reviewed release-readiness checklist.

## If onboarding is blocked

Add the tool, environment, requested group, observed error, and trace identifier if available to the access ticket. Notify your buddy and Omar through `#hpg-onboarding`. Do not request someone else's account, disable MFA, or copy production data to finish a sandbox exercise.

Use the [role ownership guide](02_team_roles_and_ownership.md) and [known issues](19_jira_known_issues_and_troubleshooting.md) to find the right escalation.
