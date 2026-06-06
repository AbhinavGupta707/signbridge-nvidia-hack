# Web App

The web app is the first-screen interpreter experience.

Initial target:

- Connect to mock WebSocket events.
- Show captions, recognised signed meaning, confirmation controls, policy cards, question prompts, and record export.
- Do not build a marketing page.

## Local Dev

This app is intentionally dependency-light for hackathon reliability.

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

By default the app connects to the integration mock:

```text
ws://127.0.0.1:8000/ws?replay=scripted&delay_scale=0.35
```

Pass a different mock WebSocket with:

```text
http://127.0.0.1:5173/?ws=ws://127.0.0.1:8000/ws?replay=scripted
```

If the orchestrator is offline, the browser runs a local contract-shaped scripted replay so the demo surface remains usable.

## Checks

```bash
npm run check
npm run build
```
