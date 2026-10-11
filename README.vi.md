# Khoa Hoang: hồ sơ kỹ thuật

Tôi xây các hệ thống AI chạy cục bộ, ghi ra những gì model giả định và kiểm tra đầu ra của nó bằng
một thứ không dùng chung giả định nào với model. Repo này chứa các bài phân tích kỹ thuật, các bảng
benchmark và hai đoạn code mẫu nhỏ. Mọi trang đều có tiếng Anh và tiếng Việt; file tiếng Việt có
đuôi `.vi`.

## Các dự án

| Dự án | Nó làm gì | Công nghệ | Hiện trạng |
|---|---|---|---|
| gen-system | Đọc codebase thành một graph deterministic dựng từ AST, liệt kê những gì model giả định về từng hàm, rồi kiểm tra code sinh ra từ bên ngoài | Go, model chạy cục bộ qua Ollama, graph RAG | Mã nguồn mở, Apache-2.0 |
| poselab-mcp | Một MCP server trả cho model các câu trả lời không gian có đo đạc khi tạo dáng tay góc nhìn thứ nhất cầm súng trường trong Blender: phần nào lấn vào nhau sâu bao nhiêu, một bề mặt hướng về mắt đến mức nào, và một bộ giải tìm cách di chuyển khẩu súng | Python, MCP, Blender chạy ngầm | Mã nguồn mở, MIT, phiên bản 0.4.0 |
| Beastwarden | Game tactics roguelite với lõi mô phỏng deterministic theo seed. Đây cũng là nơi tôi điều khiển việc lập trình có AI hỗ trợ theo các quy tắc do máy kiểm tra | TypeScript, Vite, Pixi, Vitest | Đang phát triển, riêng tư |
| HieuLuat | Hỏi đáp pháp luật tiếng Việt, viện dẫn điều luật đã dùng, hoặc nói rõ là không biết | Python, pgvector, embedding bge-m3, rerank bằng cross encoder | Ngừng phát triển sau khi công ty được mua lại |

### Liên kết

- gen-system:
- MCP server của gen-system: [gói npm `gen-understand`](https://www.npmjs.com/package/gen-understand)
  · [tài liệu](https://github.com/hpdkhoa/gen-system/blob/main/docs/mcp.md)
- poselab-mcp: [GitHub](https://github.com/hpdkhoa/poselab-mcp)
  · [PyPI](https://pypi.org/project/poselab-mcp/)
  · [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.hpdkhoa/poselab-mcp)
- Beastwarden:

## gen-system qua các con số

Tôi đo các số này trên một card RTX 4060 Ti 16 GB, trong đợt chạy ngày 2026-09-09.

- Phân giải 100% lời gọi nội bộ, 0 lỗi parse, trên bốn repo công khai: 405 file, trong đó
  268 file COBOL.
- Token đầu tiên sau 127 ms khi bật streaming, so với 1.884 ms khi gọi chờ trọn kết quả. Sớm
  hơn mười lăm lần.
- 30,8 token mỗi giây với mức offload GPU mặc định của Ollama, so với 7,9 khi chỉ đưa 20 layer
  lên GPU. Nhanh gần gấp bốn.
- Khoảng 2 giây để đổi giữa hai model trên một card 16 GB, nhờ keep alive.
- Recall file 0,674 trên 60 task của SWE-bench Verified, ở hai bước nhảy trên graph. Con số này
  đo việc gen-system tìm đúng các file mà bản sửa chạm tới. gen-system không viết bản sửa.
- Độ phủ test là 55% tổng số câu lệnh, theo `go test -cover` ngày 2026-10-08. Phần lõi cao
  hơn: control flow graph 93%, belief 85%, symbol index 76%, parser 72%.

## poselab-mcp qua các con số

Năm bài tạo dáng, mỗi bài chạy ba lần. Chính các phép đo của Pose Lab chấm từng lần chạy.

- Đạt 15 trên 15 khi có câu trả lời đo đạc, so với 11 trên 15 khi chỉ có hình ảnh.
- Một nửa số lần gọi tool (17,3 so với 34,8 mỗi bài) và một phần ba thời gian (45 giây so
  với 153 giây).

## Bài phân tích kỹ thuật

- [01, làm đường tìm kiếm pháp luật nhanh mà vẫn đúng](writeups/01-hieuluat-retrieval-optimization.vi.md).
  Đánh index vector, retrieve rồi rerank, embedding FP16, và mỗi bước tốn bao nhiêu phần của một
  request. HieuLuat đã ngừng phát triển sau khi công ty được mua lại; tôi giữ lại bài viết để ghi
  nhận phương pháp.
- [02, tinh chỉnh inference LLM cục bộ cho một code engine](writeups/02-gen-system-inference-optimization.vi.md).
  Offload layer lên GPU, streaming, coi quantization là một biến có đo, và hai model dùng chung một
  card 16 GB.
- [03, benchmark lặp lại được và cổng chặn hồi quy](writeups/03-reproducible-benchmarking.vi.md).
  Baseline đóng băng, cổng chặn hồi quy, chạy lặp lại được, và một chỉ số chất lượng có thể xê dịch.

Mỗi bài đều có một mục về chỗ tôi làm sai. Ở 01, reranker tốn 384 ms mà không cải thiện gì. Ở 02,
chỉ số chất lượng của tôi không thể xê dịch, nên nó không bao giờ báo hỏng.

Các bài cũng có bản HTML trên [trang chính](index.html).

## Benchmark

Các bảng số đằng sau các bài viết nằm trong
[benchmarks/results/measured.json](benchmarks/results/measured.json), và
[benchmarks/README.vi.md](benchmarks/README.vi.md) giải thích cách đọc chúng. File
[benchmarks/ENVIRONMENT.vi.md](benchmarks/ENVIRONMENT.vi.md) ghi lại máy chạy các bảng gen-system.

## Đoạn code mẫu

Hai file Python nhỏ chạy trên dữ liệu đồ chơi, không cần thư viện ngoài:

```bash
python snippets/toy_retrieval.py
python snippets/roofline_demo.py
```

`toy_retrieval.py` chạy retrieve rồi rerank trên vector ngẫu nhiên, và cho thấy vì sao phải đo
recall của một index xấp xỉ. `roofline_demo.py` so sánh nhân ma trận naive với dạng chia block,
viết bằng Python thuần, nên bạn thấy bức tường bộ nhớ mà không cần GPU. Xem
[snippets/README.vi.md](snippets/README.vi.md).

## Kế tiếp

Một CUDA kernel tôi tự viết bên trong gen-system, đo bằng Nsight trước và sau, kèm phân tích
roofline. Đoạn nó nhắm tới chiếm chưa tới 1 ms trong một request 385 ms, nên mục tiêu là kỹ năng,
còn tốc độ request gần như giữ nguyên.

## Người viết

Khoa Hoang. Tôi làm một năm ở National Australia Bank, rồi hai năm rưỡi ở FPT Software với vai trò
solution architect, chuyển các hệ thống cũ sang kiến trúc cloud native.

Ở đó, không ai nói được hệ thống cũ làm gì, còn những người từng biết thì đã nghỉ từ lâu. Một model
AI cũng gặp đúng chuyện đó với codebase, và bạn chỉ phát hiện ra khi đầu ra đã sai. Từ tháng 11 năm
2025 tôi toàn thời gian xây hệ thống của mình. Mỗi hệ thống ghi ra những gì model giả định, rồi chạy
một phép kiểm tra có thể báo hỏng.

[hpdkhoa2311@gmail.com](mailto:hpdkhoa2311@gmail.com) · [github.com/hpdkhoa](https://github.com/hpdkhoa)

## Giấy phép

Xem [LICENSE](LICENSE). Bạn có thể đọc và trích dẫn các bài viết, bảng số và đoạn code mẫu kèm ghi
nguồn. gen-system (Apache-2.0) và poselab-mcp (MIT) có giấy phép riêng trong repo của chúng. Phần
cài đặt của HieuLuat là tài sản riêng, và repo này không chứa nó.
