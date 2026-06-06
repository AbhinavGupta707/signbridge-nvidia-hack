# Kickoff Guide

## Recommended Startup Sequence

Yes, this project needs one initial scaffolding session before parallel feature work. That session is this repo setup plus contracts and branch protocol. After this lands on GitHub, start parallel work from the named branches in `docs/BRANCHING_AND_PARALLEL_AGENTS.md`.

## Step 1: Integration Lead

Start a Codex session on `agent/integration-scaffold`.

Prompt:

```text
You are the integration lead for Signbridge. Read IMPLEMENTATION_PLAN.md and docs/BRANCHING_AND_PARALLEL_AGENTS.md. Build the repo scaffold, shared event schemas, mock orchestrator, health endpoint, and mock WebSocket replay. Do not implement feature internals. Keep the mock demo working and preserve branch boundaries.
```

Exit criteria:

- Shared schemas exist.
- Mock orchestrator runs.
- A scripted event replay can drive the frontend later.
- Other agents have examples they can consume.

## Step 2: Parallel Feature Sessions

Start these after the integration branch has pushed contracts or after the current placeholder contracts are accepted:

```text
agent/runtime-activation
agent/vision-recognition
agent/voice-llm
agent/advocacy-data
agent/frontend-demo-ux
agent/demo-safety-pitch
```

Each session should read:

- `IMPLEMENTATION_PLAN.md`
- `docs/BRANCHING_AND_PARALLEL_AGENTS.md`
- `packages/contracts/README.md`
- `docs/RESEARCH_AND_DATA_CHECKS.md`
- its own ownership section in the implementation plan

## Step 3: Merge and Integrate

Merge into `main` only when:

- The branch passes its acceptance criteria.
- It does not change event contracts without integration lead approval.
- It has a mock-compatible mode.
- It documents any activation/provider blocker.

## Immediate Kickoff Choice

Use this order:

1. Create/push GitHub repo.
2. Start `agent/integration-scaffold`.
3. Once contracts are stable, spawn the other six branches.
4. Merge feature branches back through PRs.

