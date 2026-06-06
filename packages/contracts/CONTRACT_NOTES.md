# Contract Notes

## 2026-06-06 - v0.1 integration scaffold

The original placeholder schema only required the `type` field. This scaffold tightens validation by requiring the fields shown in `IMPLEMENTATION_PLAN.md` for each event type.

Why this changed:

- Parallel agents need examples that fail fast when a payload is incomplete.
- The frontend branch needs stable `recognition`, `translation`, `caption`, `policy`, `question`, and `record` payloads before real services exist.
- The orchestrator needs one validator shared by Python services and TypeScript clients.

What did not change:

- No event type was renamed or removed.
- No real vision, voice, advocacy RAG, or frontend internals were added.
- Mock-only `demo.replay` remains a control event for local scripted replay.

## 2026-06-06 - advocacy source trail fields

The advocacy branch emits source-backed `policy.card` and `question.prompt` events with additive citation metadata. The shared schema now explicitly allows these top-level fields while keeping `additionalProperties: false`:

- `citations`
- `policy_domain`
- `policy_card_ids`
- `verified`

`record.exported` remains a transport event containing `session_id`, `format`, and `export_url`; full record JSON/HTML exports live as separate artifacts.
