# Contracts

This folder is the shared contract layer for all parallel agents.

Rules:

- Do not rename event types without integration lead approval.
- Prefer additive optional fields, but add them to `events.schema.json` and `src/events.ts` together because the schema rejects unknown top-level fields.
- Every service must be able to run against mock events.
- Event payloads should be JSON serializable and stable across Python and TypeScript.

## Files

- `events.schema.json` is the canonical JSON Schema.
- `src/events.ts` exposes TypeScript event unions for frontend agents.
- `signbridge_contracts.py` exposes Python validation helpers for service agents.
- `examples/client.events.json` contains valid client-to-server examples.
- `examples/scripted_demo.server.events.json` contains the mock replay stream that a frontend can consume.
- `CONTRACT_NOTES.md` documents the v0.1 stabilization from the loose placeholder schema to event-specific required fields.

## Validate

From the repo root:

```bash
make validate-contracts
```

Or directly:

```bash
python3 -m packages.contracts.validate packages/contracts/examples/client.events.json packages/contracts/examples/scripted_demo.server.events.json
```

## Python Usage

```python
from packages.contracts import validate_event

validate_event({"type": "demo.replay", "session_id": "demo-001", "scenario": "housing_repair"})
```

## TypeScript Usage

```ts
import type { ServerEvent } from "@signbridge/contracts/events";

function handleEvent(event: ServerEvent) {
  if (event.type === "translation.final") {
    console.log(event.text);
  }
}
```

## Contract Change Note

The v0.1 scaffold intentionally tightened the placeholder schema so each event type requires its expected fields from `IMPLEMENTATION_PLAN.md`. No event names were removed or renamed.
