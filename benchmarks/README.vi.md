[English](README.md) · **Tiếng Việt**

# Benchmark

Mọi con số các writeup trích dẫn đều đến từ một lần chạy có ghi lại. Thư mục này giữ những con số
đó.

`results/measured.json` chứa các bảng kết quả đo. Chính harness của các dự án ghi ra file này. `tools/fill_portfolio.py` sinh các bảng trong writeup từ file này.
Vì vậy bảng trong writeup và JSON ở đây không thể lệch nhau.

## Xuất xứ từng bảng

**gen-system.** `bench/summarise.py` trong [repo gen-system](https://github.com/hpdkhoa/gen-system)
gộp các lần chạy benchmark thô trong `results/<date>/raw/` thành các dòng, rồi hợp nhất chúng vào đây. Mọi
bảng gen-system trong repo này đến từ một campaign, chạy ngày 2026-09-09 tại commit
`cfb0bff2` trên working tree sạch. Mỗi bảng có một khối `_provenance` ghi ngày, commit,
bộ tác vụ đã đóng băng và GPU. Các dòng có `n`. Ở những chỗ harness đã đo, dòng có thêm giá trị min và max.
Ô ghi n/a nghĩa là harness không đo giá trị đó. Nó không phải số 0 đã làm tròn.

Thư mục kết quả của campaign trong repo gen-system còn có hai file để người khác tự dựng lại các dòng số:

- `ATTESTATION.md` ghi những gì đã chạy, trên commit và máy nào, những lần chạy nào bị loại và ghi là
  không đo cùng lý do, và những gì đã không chạy.
- `MANIFEST.sha256` liệt kê mọi file thô kèm hash của nó.

**HieuLuat.** Bench retrieval của HieuLuat đã ghi các dòng index, rerank và embedding vào tháng 8 năm 2026, mỗi
cấu hình một nhãn, trên một bộ dữ liệu đánh giá cố định. Harness đó nằm trong repo HieuLuat riêng tư.
Vì vậy các dòng này có ngày và bộ dữ liệu đánh giá, nhưng không có commit công khai, không có cột `n`,
và không có manifest. Tôi để nguyên như harness của sản phẩm đã báo cáo.

## Môi trường đo

[`ENVIRONMENT.md`](ENVIRONMENT.vi.md) ghi lại GPU, driver, phiên bản Ollama và Go,
commit, và các mô hình có mặt khi campaign gen-system được đóng băng, kèm thời điểm ghi nhận.

## Cách đọc bảng

- `tokens per sec` là thông lượng decode do Ollama báo cáo cho lần chạy, lấy trung bình trên `n` lần chạy.
- `vram gb` là mức VRAM đỉnh do driver lấy mẫu trong lần chạy.
- `stub rate pct` là tỷ lệ các thao tác do mô hình viết đã trượt compile gate hai lần và
  bị thay bằng một stub tường minh. Đây là tín hiệu chất lượng. Tỷ lệ compile đạt là 100 phần trăm
  do chính cách thiết kế, và không được lập thành bảng.
- Các bảng SWE-bench là recall định vị trên 60 tác vụ đầu tiên của SWE-bench Verified. Chúng không phải tỷ lệ giải được. Cột kích thước vùng lân cận nằm ngay cạnh recall, vì một con số
recall chỉ có nghĩa khi bạn biết cuộc tìm kiếm đã trả về bao nhiêu file.
