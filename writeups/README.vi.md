[English](README.md) · **Tiếng Việt**

# Bài phân tích kỹ thuật

Mỗi chủ đề một bài: kiến trúc, và những con số harness báo về. Mỗi bài có bản markdown để
GitHub hiển thị trực tiếp, và một trang HTML khép kín. [Trang chủ](../index.html)
có liên kết tới các bản HTML.

| Bài | Markdown | HTML |
|---|---|---|
| Làm cho luồng tìm kiếm pháp luật nhanh mà vẫn đúng | [.md](01-hieuluat-retrieval-optimization.vi.md) | [.html](01-hieuluat-retrieval-optimization.vi.html) |
| Tinh chỉnh inference LLM cục bộ cho một công cụ xử lý code | [.md](02-gen-system-inference-optimization.vi.md) | [.html](02-gen-system-inference-optimization.vi.html) |
| Benchmark tái lập được và regression gate | [.md](03-reproducible-benchmarking.vi.md) | [.html](03-reproducible-benchmarking.vi.html) |

Mọi bảng trong các bài đều sinh ra từ [`benchmarks/results/measured.json`](../benchmarks/results/measured.json).
Các dòng gen-system ghi ngày, commit, bộ tác vụ đã đóng băng, `n` và khoảng giá trị. Manifest và
attestation của campaign nằm trong repo gen-system. Các dòng HieuLuat ghi
ngày, bộ dữ liệu đánh giá và GPU, vì harness của chúng là riêng tư. Thông tin môi trường nằm trong
[`benchmarks/ENVIRONMENT.md`](../benchmarks/ENVIRONMENT.vi.md). Các trang HTML mở được trên máy bằng
trình duyệt. Chỉ có font là tải từ CDN.
