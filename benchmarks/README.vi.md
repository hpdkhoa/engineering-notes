[English](README.md) · **Tiếng Việt**

# Benchmark

Thư mục này giữ các bảng số đo mà các writeup trích dẫn.

`results/measured.json` chứa các bảng. Harness benchmark của từng dự án ghi các dòng của dự án đó.

## Xuất xứ từng bảng

**gen-system.** `bench/summarise.py` trong [repo gen-system](https://github.com/hpdkhoa/gen-system)
gộp các lần chạy benchmark thô trong `results/<date>/raw/` thành các dòng, rồi hợp nhất chúng vào đây. Mọi
bảng gen-system ở đây đến từ một campaign ngày 2026-09-09, chạy trên working tree sạch. Mỗi bảng
ghi ngày đo, bộ tác vụ và GPU. Các dòng có `n`. Ở những chỗ harness đã đo, dòng có thêm giá trị min và max.
Ô ghi n/a nghĩa là harness không đo giá trị đó. Nó không phải số 0 đã làm tròn.

Repo gen-system giữ các file thô của campaign đó, một ghi chú về những gì đã chạy và những gì tôi đã loại,
cùng hash của từng file. Với chúng, ai cũng dựng lại được các dòng số.

**HieuLuat.** Bench retrieval của HieuLuat đã ghi các dòng index, rerank và embedding vào tháng 8 năm 2026, mỗi
cấu hình một nhãn, trên một bộ dữ liệu đánh giá cố định. Harness đó là riêng tư, nên các dòng này chỉ ghi ngày
và bộ dữ liệu đánh giá. Chúng không có số lần chạy và không có khoảng giá trị.

## Môi trường đo

[`ENVIRONMENT.md`](ENVIRONMENT.vi.md) ghi lại GPU, driver, phiên bản Ollama và Go,
và các model trên máy đã chạy campaign gen-system.

## Cách đọc bảng

- `tokens per sec` là thông lượng decode do Ollama báo cáo cho lần chạy, lấy trung bình trên `n` lần chạy.
- `vram gb` là mức VRAM đỉnh do driver lấy mẫu trong lần chạy.
- `stub rate pct` là tỷ lệ các thao tác do mô hình viết đã trượt compile gate hai lần, nên
  gen-system đặt một stub tường minh vào chỗ của chúng. Đây là tín hiệu chất lượng. Tỷ lệ compile đạt
  là 100 phần trăm do chính cách thiết kế, nên không bảng nào ghi nó.
- Các bảng SWE-bench là recall định vị trên 60 tác vụ đầu tiên của SWE-bench Verified. Chúng không phải tỷ lệ giải được. Cột kích thước vùng lân cận nằm ngay cạnh recall, vì một con số
recall chỉ có nghĩa khi bạn biết cuộc tìm kiếm đã trả về bao nhiêu file.
