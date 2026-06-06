# Branching and Parallel Agent Workflow

This project is designed for multiple Codex sessions working in parallel without conflicts.

## Ground Rules

1. `main` is the integration branch. No feature work happens directly on `main`.
2. The integration lead owns shared contracts, root configuration, and merge order.
3. Each parallel session works in exactly one feature branch.
4. Branches must keep to their declared file ownership unless the integration lead approves a contract change.
5. All components must run against mocks before expecting another branch to be merged.
6. Pull frequently from `main` and rebase or merge before opening a PR.
7. Every PR must include a short validation note and any missing provider/access assumptions.
8. If a capability is missing or unavailable, first check registration, discovery, install state, and official activation flows. Only debug runtime or permissions after the feature is actually present.

## Branch Names

Use these branches for the initial parallel work:

- `agent/integration-scaffold`
- `agent/runtime-activation`
- `agent/vision-recognition`
- `agent/voice-llm`
- `agent/advocacy-data`
- `agent/frontend-demo-ux`
- `agent/demo-safety-pitch`

## Ownership Map

| Branch | Owner role | Primary paths | Avoid touching |
|---|---|---|---|
| `agent/integration-scaffold` | Integration lead | `packages/contracts/**`, `services/orchestrator/**`, root scripts | Feature internals except mocks |
| `agent/runtime-activation` | Hardware/runtime | `infra/**`, `.env.example`, `docs/runtime/**` | Event schemas |
| `agent/vision-recognition` | Vision | `services/vision/**`, `data/landmarks/**`, `demo/clips/**` | Frontend layout, voice providers |
| `agent/voice-llm` | Voice/LLM | `services/voice/**`, translation provider files | Vision model internals |
| `agent/advocacy-data` | Policy/data agents | `services/advocacy/**`, `data/raw/**`, `docs/sources/**` | UI layout, event schema names |
| `agent/frontend-demo-ux` | Frontend | `apps/web/**` | Backend provider internals |
| `agent/demo-safety-pitch` | Demo/pitch | `demo/**`, `docs/OPEN_FLAGS.md` | Runtime code |

## Contract Change Protocol

Contracts live in `packages/contracts/**`.

Only the integration lead changes event names, required fields, or message semantics. Other branches may propose additive optional fields in PR notes, but they should keep working with the current schema.

## Merge Order

1. `agent/integration-scaffold`
2. `agent/frontend-demo-ux` against mock events
3. `agent/voice-llm` using static recognition examples
4. `agent/advocacy-data` using static transcript examples
5. `agent/vision-recognition`
6. `agent/runtime-activation`
7. `agent/demo-safety-pitch`

The order can change if a branch is ready earlier, but integration must keep a working mock demo after every merge.

## PR Template

Each PR should include:

```md
## What changed

## Validation

## Provider/access assumptions

## Files intentionally touched

## Known risks or follow-ups
```

