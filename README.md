# Signbridge

Local-first British Sign Language to speech and speech to captions system for NVIDIA Hack for Impact London.

Signbridge is a blue-sky architecture build for a public-services appointment where a Deaf BSL user has no human interpreter available. The target demo is a constrained, honest, high-quality system: sign intent recognition from camera landmarks, local LLM fluency, spoken output, live captions, and policy/question/record agents grounded in London public data.

See:

- [Product specification](signbridge-product-spec.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Parallel agent workflow](docs/BRANCHING_AND_PARALLEL_AGENTS.md)
- [Kickoff guide](docs/KICKOFF.md)
- [Research and data checks](docs/RESEARCH_AND_DATA_CHECKS.md)
- [Open flags](docs/OPEN_FLAGS.md)

## Current Status

This repo starts with architecture and coordination scaffolding only. Implementation agents should work in feature branches and must respect the shared event contracts before building deeper modules.

## First Build Principle

Do architecture first, then quality. No shortcuts that undermine privacy, source-backed policy claims, demo reliability, or the ethical position that Signbridge augments but does not replace qualified interpreters.

