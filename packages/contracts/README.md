# Contracts

This folder is the shared contract layer for all parallel agents.

Rules:

- Do not rename event types without integration lead approval.
- Prefer additive optional fields.
- Every service must be able to run against mock events.
- Event payloads should be JSON serializable and stable across Python and TypeScript.

See `events.schema.json` for the initial schema.

