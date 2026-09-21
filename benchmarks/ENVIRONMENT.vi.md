[English](ENVIRONMENT.md) · **Tiếng Việt**

# Môi trường đã đo

*Được ghi nhận bởi `bench/freeze-env.sh` của gen-system ngày 2026-09-09 lúc 16:52 UTC, trên chính máy
đã đo mọi bảng gen-system trong repo này. Các giá trị giống hệt nằm trong `results/2026-09-09/env.json`
ở repo gen-system, cạnh các file thô, manifest và attestation.*

| Hạng mục | Giá trị |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Ti, 16380 MiB |
| Driver | 595.71.05 |
| Ollama | 0.24.0 |
| Go | 1.25.0, linux/amd64 |
| Commit gen-system | `cfb0bff217481e13bb3de720ddeb672a73167027`, working tree sạch |

## Các mô hình có mặt tại thời điểm ghi nhận

Các mô hình campaign đã dùng, theo kết quả `ollama list` báo cáo. Kích thước là dung lượng file trên đĩa.

| Mô hình | Kích thước | Vai trò trong các bảng |
|---|---|---|
| `qwen3:14b` | 9.3 GB | planner trong production |
| `qwen2.5-coder:14b` | 9.0 GB | coder trong production, dòng `production` của bảng quantization |
| `deepseek-coder-v2:16b-lite-instruct-q4_K_M` | 10 GB | quét quantization, Q4_K_M |
| `deepseek-coder-v2:16b-lite-instruct-q5_K_M` | 11 GB | quét quantization, Q5_K_M |
| `deepseek-coder-v2:16b-lite-instruct-q8_0` | 16 GB | quét quantization, Q8_0 |
| `llama3.1:latest` | 4.9 GB | không bảng nào dùng |
| `aisingapore/Llama-SEA-LION-v3-8B-IT:q5_k_m` | 5.7 GB | không bảng nào dùng |
| `deepseek-coder:latest` | 776 MB | không bảng nào dùng |

## HieuLuat

Các dòng HieuLuat trong `results/measured.json` được đo vào tháng 8 năm 2026 bằng bench retrieval
riêng của sản phẩm đó. Phép đo dùng một bộ dữ liệu đánh giá cố định, trên cùng card RTX 4060 Ti 16 GB,
như các khối provenance của chúng ghi lại. Harness, phiên bản driver và thư viện của nó, cùng commit,
đều nằm trong repo HieuLuat riêng tư. Vì vậy trang này không chép lại chúng. Các dòng chỉ ghi ngày,
bộ dữ liệu đánh giá và GPU.
