# Research and Data Checks

This file records the current external assumptions that should guide implementation. Re-check unstable items during the event, especially sponsor access and model runtimes.

## Confirmed Event and Hardware Points

- NVIDIA's London Tech Week 2026 page lists Hack for Impact London as a three-day, real-hardware challenge using the NVIDIA stack, with DGX Spark on-device, Nebius cloud, and ElevenLabs voice enablement.
- NVIDIA DGX Spark is built for autonomous agents and ships with DGX OS, NVIDIA AI software, GB10 Grace Blackwell, 128 GB coherent unified memory, 273 GB/s memory bandwidth, 4 TB NVMe storage, and 10 GbE plus ConnectX-7 networking.
- HP ZGX Nano G1n AI Station is also a GB10 Grace Blackwell system with NVIDIA DGX OS 7 Ubuntu 24.04, 128 GB LPDDR5x coherent unified memory, and 273 GB/s bandwidth.

## Confirmed Impact Points

- GOV.UK's BSL Report 2022 says the BSL Act 2022 legally recognises BSL as a language of England, Scotland, and Wales.
- The same GOV.UK report cites RNID's estimate that 1 in 5 people in the UK, about 12 million people, are Deaf or hard of hearing.
- The report cites around 151,000 BSL users in total, of whom 87,000 are Deaf.
- The report states BSL is not a signed version of English and that written English or subtitles are not an adequate alternative for many BSL users.

## Confirmed Voice Points

- ElevenLabs docs list Scribe v2 Realtime as a real-time speech recognition model with over 90 languages and about 150 ms partial transcription latency.
- ElevenLabs docs list Flash models as the low-latency TTS family for real-time use.
- ElevenLabs private deployment docs state private deployment docs/resources are for authorized enterprise customers.
- ElevenLabs' April 2026 local deployment blog says on-device runs directly on hardware for offline inference, but on-premise and on-device were in early access with initial releases expected in the first half of 2026.

Implication: ElevenLabs on-device must be treated as a day-one activation/discovery item. If the official activation path is not available, use local ASR/TTS fallback for the offline proof.

## Confirmed Open Data and Policy Points

- London Datastore is a Greater London Authority open data-sharing portal with over a thousand datasets for London.
- City of London Corporation has public housing policy documents relevant to damp and mould.
- The City of London damp and mould policy says homes should be dry, safe, free from hazards, and reports should be treated with empathy and respect.
- The policy says City of London will follow up each completed damp and mould repair within six months and keep records of actions taken.
- A February 2026 GOV.UK regulatory judgement says City of London Corporation owns and manages around 1,900 social housing homes, identifies serious failings around repairs/maintenance/planned improvements, and notes that 18% of homes did not meet Decent Homes Standard based on current information at inspection time.

## Primary Sources

- NVIDIA Hack for Impact London context: https://www.nvidia.com/en-gb/events/london-tech-week/
- NVIDIA DGX Spark: https://www.nvidia.com/en-us/products/workstations/dgx-spark/
- NVIDIA DGX Spark llama.cpp playbook: https://build.nvidia.com/spark/llama-cpp
- HP ZGX Nano G1n specs: https://support.hp.com/us-en/document/ish_13212147-13212192-16
- GOV.UK BSL Report 2022: https://www.gov.uk/government/publications/the-british-sign-language-bsl-report-2022/the-british-sign-language-bsl-report-2022
- ElevenLabs models: https://elevenlabs.io/docs/models
- ElevenLabs private deployment: https://elevenlabs.io/docs/developers/private-deployment/overview
- ElevenLabs local deployment blog: https://elevenlabs.io/blog/enterprise-voice-ai-deployed-locally
- London Datastore: https://data.london.gov.uk/
- City of London Damp and Mould Policy PDF: https://democracy.cityoflondon.gov.uk/documents/s211746/Damp%20and%20Mould%20Policy%20-%20appendix%204.pdf
- City of London regulatory judgement, 25 February 2026: https://www.gov.uk/government/publications/city-of-london-corporation/city-of-london-corporation-00aa-regulatory-judgement-25-february-2026

