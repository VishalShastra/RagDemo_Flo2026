# IT Setup and Access Guide

## Laptop

- Engineers receive a 14-inch laptop with 32 GB RAM. Non-engineering staff receive 16 GB RAM.
- Laptops are refreshed every 36 months.
- Personal laptops must never be used to access customer data.

## Single sign-on and MFA

- All tools use single sign-on through "OrbitID".
- Multi-factor authentication is mandatory. The only approved authenticator app is "Okta Verify".
- SMS based MFA is not allowed.

## VPN

- The company VPN is called "OrbitGate". It is required for all internal tools when you are outside the office.
- Install the OrbitGate client from the self-service portal at https://selfservice.orbitly.example.
- OrbitGate gateway for India: in.gate.orbitly.example. For Europe: eu.gate.orbitly.example.
- VPN sessions disconnect automatically after 10 hours.

## Access requests

- Request access to GitHub, Jira and Confluence through a Jira ticket in the project "ITHELP".
- Use the request type "New Joiner Access Bundle". Standard SLA is 1 business day.
- Production database access requires manager approval plus a Security team approval and is valid for 30 days only.

## Developer tooling

- Default IDE: VS Code. JetBrains licenses are available on request.
- Container runtime: Podman Desktop (Docker Desktop is not licensed at Orbitly).
- Internal package mirror: https://artifacts.orbitly.example
