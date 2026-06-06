.PHONY: dev dev-hybrid dev-orchestrator health replay-smoke flow-smoke ws-flow-smoke prehardware-check validate-contracts

ORCHESTRATOR_HOST ?= 127.0.0.1
ORCHESTRATOR_PORT ?= 8000

dev: dev-orchestrator

dev-orchestrator:
	python3 -m uvicorn services.orchestrator.app:app --host $(ORCHESTRATOR_HOST) --port $(ORCHESTRATOR_PORT) --reload

dev-hybrid:
	SIGNBRIDGE_ORCHESTRATOR_MODE=hybrid python3 -m uvicorn services.orchestrator.app:app --host $(ORCHESTRATOR_HOST) --port $(ORCHESTRATOR_PORT) --reload

health:
	SIGNBRIDGE_ORCHESTRATOR_URL=http://$(ORCHESTRATOR_HOST):$(ORCHESTRATOR_PORT) python3 -m services.orchestrator.tools.health_check

replay-smoke:
	SIGNBRIDGE_ORCHESTRATOR_WS=ws://$(ORCHESTRATOR_HOST):$(ORCHESTRATOR_PORT)/ws python3 -m services.orchestrator.tools.ws_replay_smoke

flow-smoke:
	SIGNBRIDGE_ORCHESTRATOR_MODE=hybrid python3 -m services.orchestrator.tools.direct_flow_smoke

ws-flow-smoke:
	SIGNBRIDGE_ORCHESTRATOR_WS=ws://$(ORCHESTRATOR_HOST):$(ORCHESTRATOR_PORT)/ws python3 -m services.orchestrator.tools.ws_flow_smoke

validate-contracts:
	python3 -m packages.contracts.validate packages/contracts/examples/client.events.json packages/contracts/examples/scripted_demo.server.events.json

prehardware-check: validate-contracts
	python3 -m packages.contracts.validate services/advocacy/examples/housing_repair_demo_events.json
	python3 services/advocacy/scripts/validate_advocacy.py
	python3 -m services.voice.tools.voice_smoke --mock
	python3 -m services.voice.tools.voice_smoke
	$(MAKE) flow-smoke
	python3 -m unittest services.vision.tests.test_recognizer
	python3 -m services.vision.scripts.evaluate_recognizer --use-mock-fixture --method dtw
	cd apps/web && npm run check
	cd apps/web && npm run build
	bash -n infra/scripts/runtime_inventory.sh infra/scripts/probe_llm_runtime.sh infra/scripts/probe_voice_activation.sh infra/scripts/offline_preflight.sh
