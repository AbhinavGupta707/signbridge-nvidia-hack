# NVIDIA NIM / Ollama / llama.cpp Discovery Plan

Signbridge needs one local OpenAI-compatible LLM endpoint for gloss-to-English rewriting and agent prompts. First working local runtime wins. Do not change event contracts to fit a provider.

## Target Interface

Set these variables once a runtime is selected:

```bash
LLM_PROVIDER=nim|ollama|llama_cpp|local_openai
LLM_BASE_URL=http://<runtime-host>:<port>/v1
LLM_MODEL=<served-model-id>
```

Validate with:

```bash
infra/scripts/probe_llm_runtime.sh "$LLM_BASE_URL" "$LLM_MODEL"
```

## Decision Order

1. Use NIM if NGC registration, NIM entitlement, container runtime, and model probe all pass.
2. Use Ollama if it is already installed/activated through the DGX Spark playbook and serves a suitable local model quickly.
3. Use llama.cpp if source build and GGUF model download are faster or more reliable than NIM/Ollama activation.
4. Use mock only for integration plumbing. Mock is not an offline inference proof.

## NIM Discovery

Official path:

- NVIDIA Spark NIM playbook: https://build.nvidia.com/spark/nim-llm
- NVIDIA NIM LLM docs: https://docs.nvidia.com/nim/large-language-models/1.5.0/getting-started.html

Layer checks:

- Registration: NGC account exists, NGC API key is available, required NIM catalog item is accessible.
- Discovery: selected NIM image and model are listed for Spark/GB10 or confirmed by event staff.
- Install state: Docker and NVIDIA Container Toolkit are installed.
- Runtime: NIM container starts and exposes `/v1/models`.
- App integration: `LLM_BASE_URL` points to the NIM `/v1` endpoint.

Useful commands:

```bash
nvidia-smi
docker run --rm --gpus all nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04 nvidia-smi
echo "$NGC_API_KEY" | grep -E '^[a-zA-Z0-9]{86}==$'
curl -fsS "$NIM_BASE_URL/models"
```

Block precisely if:

- NGC key is missing.
- NIM image is not entitled.
- Docker GPU test fails.
- `/v1/models` does not respond after container startup.

## Ollama Discovery

Official paths:

- DGX Spark playbooks: https://build.nvidia.com/spark
- Ollama Linux docs: https://docs.ollama.com/linux
- Ollama GPU docs: https://docs.ollama.com/gpu
- Ollama OpenAI compatibility: https://docs.ollama.com/openai

Layer checks:

- Registration: DGX Spark or ZGX Nano is reachable; Ollama path is approved for the event device.
- Discovery: Ollama is installed and `ollama --version` works.
- Install state: target model is present in `ollama list`.
- Runtime: `ollama serve` is reachable on LAN and model responds.
- App integration: use OpenAI-compatible base URL, usually `http://<host>:11434/v1`.

Useful commands:

```bash
ollama --version
ollama list
ollama pull qwen3.6:35b-a3b-nvfp4
OLLAMA_HOST=0.0.0.0:11434 ollama serve
curl -fsS http://127.0.0.1:11434/api/tags
```

Candidate env:

```bash
LLM_PROVIDER=ollama
LLM_BASE_URL=http://<spark-host>:11434/v1
LLM_MODEL=qwen3.6:35b-a3b-nvfp4
```

If Ollama falls back to CPU, confirm GPU discovery and install state first. Ollama docs note Linux suspend/resume can affect NVIDIA GPU discovery; only use driver workarounds after installation and model presence are confirmed.

## llama.cpp Discovery

Official path:

- NVIDIA Spark llama.cpp playbook: https://build.nvidia.com/spark/llama-cpp

Layer checks:

- Registration: DGX Spark/ZGX Nano is assigned and reachable.
- Discovery: source checkout, CMake, CUDA toolkit, and GGUF model target are known.
- Install state: `llama-server` exists after a CUDA build.
- Runtime: `llama-server` listens on a LAN port and exposes OpenAI-compatible endpoints.
- App integration: `LLM_BASE_URL` points to the llama.cpp `/v1` endpoint.

Useful commands from the official flow:

```bash
git --version
cmake --version
nvcc --version
cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121" -DLLAMA_CURL=OFF
./bin/llama-server --model ~/models/<model>/<model-file>.gguf --host 0.0.0.0 --port 30000 --n-gpu-layers 99 --ctx-size 8192 --threads 8
curl -fsS http://127.0.0.1:30000/v1/models
```

Candidate env:

```bash
LLM_PROVIDER=llama_cpp
LLM_BASE_URL=http://<spark-host>:30000/v1
LLM_MODEL=nemotron
```

## Model Selection Notes

Keep the first demo model conservative:

- Good enough for short controlled rewrites.
- Fits comfortably in GB10 unified memory with room for orchestrator, retrieval, and voice fallback.
- Downloaded before the offline proof.
- Does not require public egress at inference time.

The current planning docs mention Qwen3.6-35B-A3B and NVIDIA Nemotron examples. Use whichever is available through the selected runtime first; do not lose demo time chasing a preferred model after another local model is already responding.

## Runtime Selection Record

Add this to PR notes:

```md
## Runtime Selection

- Selected provider:
- Base URL:
- Model:
- Probe command:
- Probe result:
- Offline eligible: yes/no
- Known limitation:
- Fallback if it fails during demo:
```
