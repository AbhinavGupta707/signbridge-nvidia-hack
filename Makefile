.PHONY: dev dev-orchestrator health replay-smoke validate-contracts

ORCHESTRATOR_HOST ?= 127.0.0.1
ORCHESTRATOR_PORT ?= 8000

dev: dev-orchestrator

dev-orchestrator:
	python3 -m uvicorn services.orchestrator.app:app --host $(ORCHESTRATOR_HOST) --port $(ORCHESTRATOR_PORT) --reload

health:
	SIGNBRIDGE_ORCHESTRATOR_URL=http://$(ORCHESTRATOR_HOST):$(ORCHESTRATOR_PORT) python3 -m services.orchestrator.tools.health_check

replay-smoke:
	SIGNBRIDGE_ORCHESTRATOR_WS=ws://$(ORCHESTRATOR_HOST):$(ORCHESTRATOR_PORT)/ws python3 -m services.orchestrator.tools.ws_replay_smoke

validate-contracts:
	python3 -m packages.contracts.validate packages/contracts/examples/client.events.json packages/contracts/examples/scripted_demo.server.events.json
