# Measured environment

*Captured by gen-system's `bench/freeze-env.sh` on 2026-09-09 at 16:52 UTC, on the machine every
gen-system table in this repository was measured on. The same values are in `results/2026-09-09/env.json`
in the gen-system repository, beside the raw files, the manifest and the attestation.*

| What | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Ti, 16380 MiB |
| Driver | 595.71.05 |
| Ollama | 0.24.0 |
| Go | 1.25.0, linux/amd64 |
| gen-system commit | `cfb0bff217481e13bb3de720ddeb672a73167027`, working tree clean |

## Models present at capture

The models the campaign used, as `ollama list` reported them. Sizes are the files on disk.

| Model | Size | Role in the tables |
|---|---|---|
| `qwen3:14b` | 9.3 GB | production planner |
| `qwen2.5-coder:14b` | 9.0 GB | production coder, the `production` row of the quantization table |
| `deepseek-coder-v2:16b-lite-instruct-q4_K_M` | 10 GB | quantization sweep, Q4_K_M |
| `deepseek-coder-v2:16b-lite-instruct-q5_K_M` | 11 GB | quantization sweep, Q5_K_M |
| `deepseek-coder-v2:16b-lite-instruct-q8_0` | 16 GB | quantization sweep, Q8_0 |
| `llama3.1:latest` | 4.9 GB | not used by any table |
| `aisingapore/Llama-SEA-LION-v3-8B-IT:q5_k_m` | 5.7 GB | not used by any table |
| `deepseek-coder:latest` | 776 MB | not used by any table |

## HieuLuat

The HieuLuat rows in `results/measured.json` were measured in August 2026 by that product's own
retrieval bench, against a fixed evaluation set, on the same RTX 4060 Ti with 16 GB, as their
provenance blocks record. The harness, its driver and library versions, and the commit are in the
private HieuLuat repository, so this page does not reproduce them. The rows carry the date, the
evaluation set and the GPU only.
