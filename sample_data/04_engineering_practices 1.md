# Engineering Practices

## Source control

- Git hosting: GitHub Enterprise, organization "orbitly".
- Branch naming: `<jira-key>-<short-description>`, for example `ORB-1427-fix-vpn-timeout`.
- Every pull request needs 2 approvals, one of them from a code owner.
- Squash merge only. Force pushes to `main` are blocked.

## CI/CD

- CI runs on GitHub Actions. The pipeline must be green before merge.
- Production deployments happen through the internal tool "LaunchControl".
- Deploy windows: Monday to Thursday, 10:00 to 16:00 IST. No deployments on Fridays.
- Code freeze: from 15 December to 5 January every year.

## On-call

- On-call rotation is called "Orbit Watch". Each rotation is 7 days, starting Wednesday at 10:00 IST.
- New joiners shadow one Orbit Watch rotation after 60 days and join the rotation after 90 days.
- On-call engineers receive an allowance of INR 2,500 per day on call.
- Incidents are declared in Slack with the command `/orbit incident`. Severity levels: SEV1 (customer down) to SEV4 (cosmetic).

## Documentation

- Architecture decisions are recorded as ADRs in the Confluence space "ENGARCH".
- Runbooks live in the Confluence space "RUNBOOKS".
