# Security and Compliance

## Data classification

- Orbitly uses four levels: Public, Internal, Confidential and Restricted.
- Customer shipment data is "Restricted". It must never leave approved systems and must never be pasted into public AI tools.
- Approved AI assistants for internal code: the internal "OrbitCopilot" gateway only.

## Passwords and secrets

- Secrets are stored in HashiCorp Vault at https://vault.orbitly.example.
- Never commit secrets to Git. The pre-commit hook "orbit-secret-scan" blocks commits that contain keys.

## Incident reporting

- Report a suspected security incident within 1 hour by emailing security@orbitly.example or posting in #sec-incident.
- Lost or stolen laptop: report within 2 hours to the IT Help Desk (extension 4400).

## Compliance

- Orbitly is ISO 27001 certified and SOC 2 Type II audited.
- All employees must complete "SEC-AWARE-2026" within their first 7 days and then yearly.
