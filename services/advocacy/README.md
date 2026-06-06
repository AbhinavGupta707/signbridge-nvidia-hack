# Advocacy

Policy, Question, and Record agents live here.

Initial target:

- City of London housing repair / damp and mould scenario.
- Local RAG over source-backed policy pages and PDFs.
- Every policy card must include source metadata and a short quote.

## What is implemented

- Source manifest: `docs/sources/city_london_housing_repair_source_manifest.json`
- Curated verified seed corpus: `services/advocacy/corpus/verified_source_notes.json`
- Local raw preload mirror: `data/raw/advocacy/housing_repair/verified_source_notes.json` (`data/raw/` is ignored by git)
- Local JSONL retrieval index: `services/advocacy/index/housing_repair_chunks.jsonl`
- Offline lexical retriever: `signbridge_advocacy.retrieval.LocalRetriever`
- Deterministic `policy.card` and `question.prompt` generators
- Record export structure in JSON and HTML
- Source-backed demo event examples under `services/advocacy/examples/`

## Local commands

From repo root:

```bash
python3 services/advocacy/scripts/build_local_index.py
python3 services/advocacy/retrieve.py search "child asthma mould bedroom emergency" --policy-only
python3 services/advocacy/retrieve.py questions "There is damp and mould in my child's bedroom and asthma is worse. I need BSL updates."
python3 services/advocacy/demo.py --write-examples
python3 services/advocacy/scripts/validate_advocacy.py
```

## Event behavior

`PolicyAgent` emits contract-compatible `policy.card` events with the required fields:

- `type`
- `id`
- `title`
- `claim`
- `source_title`
- `source_url`
- `quote`

It also adds a `citations` array as an optional source-trail field. The shared contract explicitly includes this field; future source-trail additions must update both `packages/contracts/events.schema.json` and `packages/contracts/src/events.ts`.

`QuestionAgent` emits `question.prompt` events grounded in the policy cards that triggered them. Prompt events include `policy_card_ids` and `citations` so the Record Agent can preserve the source trail.

`RecordAgent` exports:

- transcript utterances
- policy cards and citations
- suggested questions
- commitments, when supplied by orchestrator
- evidence checklist
- verified vs needs-confirmation notes from the source manifest

## Verified vs needs confirmation

Verified for the demo:

- City of London damp/mould reporting and policy sources exist and were checked on 2026-06-06.
- City policy supports cards about reporting, response aims, vulnerability triage, accessibility, records, follow-up, complaints, and temporary accommodation.
- GOV.UK Awaab's Law guidance supports legal-context cards for covered social housing tenancies.

Still needs confirmation:

- Whether the specific resident's tenancy is covered by Awaab's Law.
- Current City contact details and web form availability on demo day.
- Complete source download/licence archiving for production ingestion.
- Exact borough-level hearing impairment or BSL-user data before making deployment-priority claims.
