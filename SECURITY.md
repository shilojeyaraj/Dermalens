# Security Policy

## Supported Versions

This project is under active development. Security fixes are applied to the
latest released version on the `main` branch.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report them privately so we can investigate and ship a fix before
details become public:

- **Email:** [shilo@coincidencelabs.com](mailto:shilo@coincidencelabs.com)
- Alternatively, use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
  ("Report a vulnerability" under the **Security** tab).

When reporting, please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof of concept if possible)
- Affected component (frontend / backend) and version or commit

## Response Targets

| Stage                | Target            |
| -------------------- | ----------------- |
| Acknowledgement      | within 3 days     |
| Initial assessment   | within 7 days     |
| Fix or mitigation    | based on severity |

We will keep you informed throughout the process and credit you in the release
notes once a fix is published, unless you prefer to remain anonymous.

## Handling Secrets

This repository never commits real credentials. Configuration is provided via
environment variables (`.env`, which is git-ignored). Use `.env.example` as a
template. If you discover a committed secret, please report it via the channel
above so it can be rotated.
