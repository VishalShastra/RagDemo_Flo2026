# Jira Export - Known Onboarding Issues (project ITHELP and ORB)

This file simulates an export of Jira tickets. Ticket keys are exact identifiers, which makes them a good test for keyword (sparse/BM25) search.

## ORB-1427 - OrbitGate VPN disconnects on Ubuntu 24.04

- Status: Resolved
- Root cause: the OrbitGate client 3.2 conflicts with systemd-resolved.
- Fix: upgrade to OrbitGate client 3.4.1 or later, then run `sudo orbitgate repair-dns`.

## ORB-1502 - New joiner cannot see the ENGARCH Confluence space

- Status: Resolved
- Fix: the "New Joiner Access Bundle" ticket must include the group `conf-engarch-readers`. Raise a follow-up ITHELP ticket if it is missing.

## ITHELP-8841 - Okta Verify push notifications not received

- Status: Workaround
- Workaround: open Okta Verify, go to Settings and choose "Re-enable push". If it still fails, use the 6-digit code option.

## ITHELP-9120 - Podman Desktop fails to start on Windows 11

- Status: Resolved
- Fix: enable the "Virtual Machine Platform" Windows feature and restart. Admin rights are granted temporarily through ticket type "Temporary Admin (2h)".

## ORB-1610 - LaunchControl shows "deploy window closed" on Thursday evening

- Status: Won't fix
- Explanation: deployments are allowed only between 10:00 and 16:00 IST from Monday to Thursday. Thursday evening deploys require a SEV1 or SEV2 exception approved by the Engineering Manager on duty.
