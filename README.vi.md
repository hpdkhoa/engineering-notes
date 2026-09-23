[English](README.md) · **Tiếng Việt**

# gen-system, HieuLuat, Beastwarden

Ba hệ thống tôi đang làm. Đây là phần tôi có thể công khai về từng hệ thống.

gen-system có [repo riêng](https://github.com/hpdkhoa/gen-system), gồm code, test và các driver
benchmark. Hai hệ thống còn lại thì tôi không mở được. HieuLuat chạy trên hồ sơ vụ việc thật của một
văn phòng luật và công ty đang chuyển nhượng, nên source, prompt và kho văn bản luật của nó vẫn nằm
nguyên chỗ cũ, còn Beastwarden mới xong một nửa. Với hai hệ thống đó, repo này chỉ có tài liệu thiết
kế và các bảng số.

Mọi thứ ở đây đều viết hai lần, tiếng Anh và tiếng Việt. File tiếng Việt có đuôi `.vi`.

## Ba hệ thống

| Hệ thống | Nó làm gì | Công nghệ | Trang |
|---|---|---|---|
| gen-system | Đọc codebase thành một graph deterministic dựng từ AST, nêu rõ mô hình giả định gì về từng hàm, rồi kiểm tra code sinh ra từ bên ngoài | Go, model chạy cục bộ qua Ollama, graph RAG | [projects/gen-system/README.vi.md](projects/gen-system/README.vi.md) |
| HieuLuat | Hỏi đáp pháp luật tiếng Việt. Mỗi câu trả lời đều viện dẫn đúng điều luật, hoặc nêu rõ là không đủ căn cứ | Python, pgvector, embedding bge-m3 trên GPU, rerank bằng cross encoder | [projects/hieuluat/README.vi.md](projects/hieuluat/README.vi.md) |
| Beastwarden | Game tactics roguelite với lõi deterministic theo seed và khoảng 2.000 test. Đồng thời là ghi chép của tôi về cách điều khiển việc lập trình có AI hỗ trợ | TypeScript, Vite, Pixi, Vitest | [projects/beastwarden/README.vi.md](projects/beastwarden/README.vi.md) |

## Bài phân tích kỹ thuật

- [01, làm đường tìm kiếm pháp luật nhanh mà vẫn đúng](writeups/01-hieuluat-retrieval-optimization.vi.md).
  Đánh index vector, retrieve rồi rerank, embedding FP16, và mỗi bước thực sự tốn bao nhiêu phần
  của một request.
- [02, tinh chỉnh inference LLM cục bộ cho một code engine](writeups/02-gen-system-inference-optimization.vi.md).
  Offload layer lên GPU, streaming, coi quantization là một biến có đo, và hai model dùng chung một
  card 16 GB.
- [03, benchmark lặp lại được và cổng chặn hồi quy](writeups/03-reproducible-benchmarking.vi.md).
  Phương pháp nằm dưới hai writeup kia: baseline đóng băng, task set commit trước, chạy lặp lại
  được.

Mỗi bài đều có một mục về chỗ tôi làm sai. Ở 01, reranker tốn 384 ms mà không cải thiện gì. Ở 02,
chỉ số chất lượng của tôi không thể xê dịch, nên nó không bao giờ báo hỏng. Tôi cứ ghi lại, nếu
không thì một năm sau tôi lại giẫm đúng vào đó.

Các bài đều là markdown. Mỗi bài còn có bản HTML, mở từ [index.html](index.html), nếu bạn thích đọc
kiểu đó hơn.

## Xuất xứ các con số

- [benchmarks/results/measured.json](benchmarks/results/measured.json) chứa mọi bảng. Harness ghi
  file đó. Tôi không gõ tay một con số nào vào writeup.
- [benchmarks/ENVIRONMENT.vi.md](benchmarks/ENVIRONMENT.vi.md) ghi lại máy chạy các bảng
  gen-system: RTX 4060 Ti 16 GB, driver 595.71.05, Ollama 0.24.0, Go 1.25.0, và commit mà campaign
  đóng băng tại đó.
- Campaign ngày 2026-09-09 giữ file thô, `MANIFEST.sha256` và `ATTESTATION.md` trong repo
  gen-system, ngay cạnh code đã tạo ra chúng.
- Dòng của gen-system mang theo ngày, commit, task set đã đóng băng, `n` và một khoảng giá trị.
  Dòng của HieuLuat mang theo ngày, tập đánh giá và GPU, vì harness đó riêng tư.
- [benchmarks/README.vi.md](benchmarks/README.vi.md) giải thích cách đọc một bảng.

## Đoạn code mẫu

Hai file Python nhỏ chạy trên dữ liệu đồ chơi, không cần thư viện ngoài:

```bash
python snippets/toy_retrieval.py
python snippets/roofline_demo.py
```

`toy_retrieval.py` chạy mẫu retrieve rồi rerank trên vector ngẫu nhiên, và cho thấy vì sao recall
của một index xấp xỉ cần đo chứ không đoán. `roofline_demo.py` so sánh nhân ma trận naive với dạng
chia block, viết bằng Python thuần, nên bạn thấy bức tường bộ nhớ mà không cần GPU. Cả hai đều
không có code production. Xem [snippets/README.vi.md](snippets/README.vi.md).

## Tái tạo repo

`tools/fill_portfolio.py` chạy trên máy của tôi, nơi có các repo riêng tư. Nó lấy thống kê repo từ
git, chụp lại môi trường bằng `nvidia-smi` và `ollama list`, rồi chèn các bảng từ `measured.json`
vào giữa các dấu `<!--measured:...-->`. Nó không bao giờ chép source vào repo này.

`tools/regen_writeup_html.py` dựng lại bản HTML của từng writeup, cả tiếng Anh và tiếng Việt. Hãy
chạy nó sau `fill_portfolio.py`, nếu không bản HTML sẽ lệch với markdown. File HTML do công cụ sinh
ra, nên hãy sửa markdown rồi chạy lại công cụ.

## Hiện trạng

- gen-system: đang chuẩn bị bản phát hành Apache-2.0.
- HieuLuat: sản phẩm thương mại, quyền sở hữu đang chuyển giao. Phần cài đặt vẫn riêng tư.
- Beastwarden: đang phát triển.
- Kế tiếp: một CUDA kernel tôi tự viết bên trong gen-system, đo bằng Nsight trước và sau, kèm phân
  tích roofline. Đoạn nó nhắm tới chiếm chưa tới 1 ms trong một request 385 ms, nên nó chứng minh
  năng lực chứ không làm request nhanh lên.

## Người viết

Khoa Hoang. Tôi làm một năm ở National Australia Bank, rồi hai năm rưỡi ở FPT Software với vai trò
solution architect, chuyển các hệ thống cũ sang kiến trúc cloud native.

Thiết kế đích hiếm khi là phần khó. Phần khó là không ai nói được hệ thống cũ thực sự làm gì, còn
những người từng biết thì đã nghỉ từ lâu. Một mô hình AI cũng vướng đúng chuyện đó với codebase, chỉ
khác là bạn phát hiện ra khi đầu ra đã sai. Từ tháng 11 năm 2025 tôi toàn thời gian xây hệ thống của
mình. Cả hai đều quay về chuyện đó: viết ra thứ mà máy đang giả định, rồi chạy một phép kiểm tra có
thể báo hỏng.

[hpdkhoa2311@gmail.com](mailto:hpdkhoa2311@gmail.com) · [github.com/hpdkhoa](https://github.com/hpdkhoa)

## Giấy phép

Xem [LICENSE](LICENSE). Các writeup, tài liệu kiến trúc, bảng benchmark và snippet ở đây để bạn đọc
và trích dẫn kèm ghi nguồn. gen-system có giấy phép riêng Apache-2.0 trong repo của nó. Phần cài
đặt của HieuLuat là tài sản riêng và không nằm trong repo này.
