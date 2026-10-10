# HarborPay Gateway: repositories, local setup, and environments

Audience: developers and QA; BAs/managers use the environment overview. Purpose: describe the fictional project setup without confusing it with this RAG repository.

All repository names, software baselines, paths, configuration, and endpoints below are fictional training data. The payment source code and setup commands are not supplied here. Do not run these instructions against the Langflow repository expecting a payment service.

## Fictional repository directory

| Repository | Owner | Contents |
|---|---|---|
| `hpg-payment-api` | Dev | Spring Boot API, provider adapter, workers, database migrations |
| `hpg-merchant-portal` | Dev | React/TypeScript portal |
| `hpg-test-suite` | Priya | Contract, integration, browser, and payment-scenario tests |
| `hpg-platform-config` | Omar | Environment templates and release manifests; no plaintext secrets |

Request access through the [joiner checklist](03_joiner_checklists_and_access.md). Illustrative clone locations use `https://git.harborpay.example`; these are not downloadable repositories.

## Example tooling baseline

The fictional backend baseline is Java 21, Spring Boot 3.5, and the repository's Maven Wrapper. The portal baseline is Node.js 22, React 19, TypeScript 5.8, and npm with its checked-in lockfile. Local data services are PostgreSQL 16 and Redis 7. The provider is MockBridge in mock mode.

These versions describe the sample project, not the dependencies needed to run the Langflow demonstration. Actual payment-project instructions would require its own manifest and supported versions.

## Local setup sequence

1. Obtain the fictional project's approved source and managed-device permissions.
2. Check the Java/Node versions against its manifests and use the checked-in wrappers.
3. Provision local PostgreSQL/Redis through the project's approved setup method; isolate them from shared data.
4. Copy the project's configuration template into an ignored local configuration file.
5. Obtain local-only credentials through the approved process; never place them in documentation or source control.
6. Apply backend migrations, load synthetic merchant fixtures, and start MockBridge in mock mode.
7. Start the backend, then the portal; verify readiness before testing checkout.
8. Run a synthetic create/authorize/capture scenario and record its operation IDs.

Illustrative configuration names: `DATABASE_URL`, `REDIS_URL`, `PROVIDER_MODE=mock`, `MOCKBRIDGE_BASE_URL`, `WEBHOOK_SECRET_REF`, and `ENVIRONMENT`. A secret reference identifies approved secret storage, not a secret value.

Example local addresses are `http://localhost:8080` for the backend and `http://localhost:3000` for the portal. The hypothetical backend readiness path is `/actuator/health/readiness`; a ready result requires database connectivity and migrations. Diagnose logs safely if readiness fails.

## Environment map

| Environment | Purpose | Data and access |
|---|---|---|
| Local | Isolated development and tests | Synthetic fixtures only |
| Sandbox | Shared integration with MockBridge | Synthetic fixtures; role-based project access |
| UAT | User acceptance testing before release | Approved synthetic business scenarios |
| Production | Hypothetical real deployment boundary | No access by default; not supplied by this demo |

Sandbox portal example: `https://portal.sandbox.harborpay.example`. UAT endpoint example: `https://api.uat.harborpay.example`. Reserved example endpoints do not resolve to usable project services.

## Setup completion and escalation

You are ready when the intended environment is identified, migrations succeed, health is ready, synthetic fixtures are available, and a role-permitted scenario runs. Attach sanitized results, not credentials. Route access/configuration blockers to Omar, code failures to Dev, and test-fixture problems to Priya.
