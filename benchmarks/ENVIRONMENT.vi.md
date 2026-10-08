[English](ENVIRONMENT.md) · **Tiếng Việt**

# Môi trường đã đo

*Máy và phần mềm đã đo mọi bảng gen-system, ghi lại ngày 2026-09-09.*

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

Bench retrieval riêng của HieuLuat đã đo các dòng của nó vào tháng 8 năm 2026, trên cùng card RTX 4060 Ti,
với một bộ dữ liệu đánh giá cố định. Bench đó là riêng tư, nên trang này không ghi phiên bản nào của nó.
