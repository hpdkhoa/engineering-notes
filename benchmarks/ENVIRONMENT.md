**English** · [Tiếng Việt](ENVIRONMENT.vi.md)

# Measured environment

*The machine and software that measured every gen-system table, recorded on 2026-09-09.*

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
| `llama3.1:latest` | 4.9 GB | no table uses it |
| `aisingapore/Llama-SEA-LION-v3-8B-IT:q5_k_m` | 5.7 GB | no table uses it |
| `deepseek-coder:latest` | 776 MB | no table uses it |

## HieuLuat

HieuLuat's own retrieval bench measured its rows in August 2026, on the same RTX 4060 Ti, against
a fixed evaluation set. That bench is private, so this page lists no versions for it.
