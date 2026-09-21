[English](README.md) · **Tiếng Việt**

# Đoạn code mẫu: các ví dụ nhỏ chạy được

Vài file Python nhỏ, tự chạy với dữ liệu mẫu, minh họa các kỹ thuật tôi dùng trong các dự án. Trong
đây không có code production, prompt, dữ liệu hay cấu hình nào của HieuLuat hoặc gen-system.

Chúng ở đây để bạn tự kiểm tra một khẳng định trong writeup, còn tôi thì không phải đưa ra thứ gì
riêng tư.

Mỗi file chạy được với bản cài Python 3 tiêu chuẩn. Chỉ cần thư viện chuẩn, cộng thêm NumPy
ở những chỗ có ghi chú. Không cần GPU, cơ sở dữ liệu hay mạng.

| File | Nội dung minh họa | Nguồn |
|---|---|---|
| `toy_retrieval.py` | Retrieve rồi rerank trên các vector giả, và lý do phải kiểm tra recall của một index | [tối ưu retrieval](../writeups/01-hieuluat-retrieval-optimization.vi.md) |
| `roofline_demo.py` | Nhân ma trận ngây thơ so với nhân theo khối, và trực giác về bộ nhớ so với tính toán | [tối ưu inference](../writeups/02-gen-system-inference-optimization.vi.md) |

Chạy trực tiếp một trong hai file:

```bash
python3 toy_retrieval.py
python3 roofline_demo.py
```

> > Đây là ví dụ để giảng giải. Hệ thống thật thì lớn hơn và lộn xộn hơn nhiều. Phần triển khai của
> HieuLuat thuộc sở hữu độc quyền, còn gen-system thì sắp phát hành theo Apache-2.0. Chạy thử hai
> file này, các khẳng định trong writeup sẽ không còn là lời nói suông.
