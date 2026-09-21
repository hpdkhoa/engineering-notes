[English](README.md) · **Tiếng Việt**

# HieuLuat: hỏi đáp pháp luật Việt Nam

> Một hệ thống trả lời câu hỏi về pháp luật Việt Nam chỉ dựa trên văn bản luật mà bước retrieval tìm
> được. Hệ thống trích dẫn nguồn. Khi corpus không chứa câu trả lời, hệ thống nói như vậy thay vì
> đoán. HieuLuat là một sản phẩm thương mại đang được chuyển giao quyền sở hữu, vì vậy code, corpus
> và prompt của nó được giữ không công khai. Trang này trình bày kiến trúc, lập luận đằng sau thiết
> kế, và những gì harness đánh giá của nó đã đo.

---

## Thông tin nhanh

- **Trạng thái:** sản phẩm đã phát hành, code không công khai. Đã xây dựng và đo trước các lần chạy
  đánh giá 2026-08 được báo cáo trong writeup; chưa chạy lại kể từ đó.
- **Pipeline:** 7 giai đoạn, giai đoạn nào cũng chạy lại được: thu thập, trích xuất, chia chunk, embedding, retrieval, rerank, trả lời
- **Corpus:** văn bản pháp luật Việt Nam từ các nguồn chính thức, chia chunk theo ranh giới điều và điều khoản
- **Công nghệ:** Python (52,783 dòng), PostgreSQL với pgvector, embedding bge-m3 trên GPU, rerank bằng cross encoder
- **Cam kết:** mọi câu trả lời đều lấy từ văn bản luật đã được retrieval và có trích dẫn. Hệ thống có sẵn một nhánh cho trường hợp "không tìm thấy thông tin"
- **Cổng chất lượng:** các eval set đã gán nhãn quyết định một tối ưu hóa có được chấp nhận hay không

## Cái gì có ở đây, cái gì không

Code, corpus pháp luật, prompt, cấu hình và dữ liệu đánh giá vẫn nằm riêng. Trang này có pipeline
kèm ranh giới từng giai đoạn, các quyết định tôi đã chọn và lý do, cùng những con số retrieval đúng
như harness của sản phẩm báo cáo, kể cả con số ra kết quả âm tính. Mỗi con số ghi kèm ngày đo và
eval set. Không con số nào ghi kèm commit công khai, vì harness nằm trong repo riêng tư.

## Vấn đề

Hỏi đáp pháp luật có một kiểu lỗi mà hệ thống thường sống chung được, còn pháp luật thì không: một
câu trả lời tự tin mà không điều khoản nào chống lưng. Người trả giá là luật sư đã nhắc lại câu đó
trước mặt khách hàng, không phải hệ thống.

Nên tiêu chuẩn không phải là nghe có vẻ đúng. Mọi nhận định phải truy được về một điều khoản có
thật, và khi corpus im lặng thì hệ thống phải nói ra. Ràng buộc đó có trước, rồi pipeline mới dựng
quanh nó.

## Pipeline

Bảy giai đoạn. Mỗi giai đoạn đều chạy lại an toàn được và kiểm thử riêng được.

1. **Thu thập.** Lấy văn bản pháp luật từ các nguồn chính thức, ghi lại xuất xứ của từng văn bản.
2. **Trích xuất.** Tách văn bản số gốc khỏi các trang scan cần OCR, và xử lý đúng cách từng loại.
   Chất lượng trích xuất quyết định mọi bước phía sau.
3. **Chia chunk.** Chia theo ranh giới điều và điều khoản, không theo số token cố định. Nhờ vậy mỗi
   chunk là một đơn vị pháp lý hoàn chỉnh có thể trích dẫn.
4. **Embedding.** Mã hóa các chunk bằng bge-m3 trên GPU vào pgvector, gắn nhãn theo họ embedding
   model và theo nguồn.
5. **Retrieval.** Tìm kiếm láng giềng gần nhất theo cosine, lọc theo nguồn và họ model.
6. **Rerank.** Một cross encoder chấm điểm lại các ứng viên mà retrieval trả về. Đây là giai đoạn
   thứ hai của thiết kế retrieval diện rộng rồi rerank.
7. **Trả lời.** Sinh câu trả lời chỉ trong phạm vi ngữ cảnh đã retrieval, có trích dẫn, và có nhánh
   "không tìm thấy thông tin" tường minh khi retrieval không trả về gì hữu ích.

## Các quyết định thiết kế và lý do

**Chia chunk theo ranh giới điều, không theo cửa sổ cố định.** Một câu trả lời pháp lý phải trích
dẫn một điều khoản. Một chunk cắt ngang hoặc nằm vắt qua nhiều điều khoản tạo ra ngữ cảnh không thể
trích dẫn. Vì vậy bộ chia chunk đi theo cấu trúc pháp lý.

**Bám nguồn được xây dựng sẵn, không lọc về sau.** Yêu cầu trích dẫn và nhánh không có thông tin là
đặc tính của chính giai đoạn trả lời. Chúng không phải một bộ lọc gắn thêm sau khi sinh câu trả lời.
Hệ thống được xây dựng sao cho khó tạo ra một câu trả lời không bám nguồn.

**Vector gắn nhãn theo nguồn và họ model.** Kho lưu trữ có thể chứa nhiều họ embedding model và văn
bản từ nhiều nguồn khác nhau. Retrieval lọc theo cả hai. Các bộ lọc đó tồn tại để bảo đảm tính đúng
đắn, không phải để tăng tốc.

**Eval set là một sản phẩm bàn giao thực sự.** Dự án bàn giao kèm các eval set đã gán nhãn. Chất
lượng được đo trên các trường hợp cố định thay vì đánh giá theo cảm tính. Một tối ưu hóa được chấp
nhận hay bị loại dựa trên các eval set đó.

## Kết quả

Phần việc về hiệu năng và chất lượng trên luồng retrieval được viết chi tiết trong một writeup.
Writeup đó bao gồm vector index, việc bật reranker và embedding FP16, cùng các đánh đổi đã đo:

→ [Làm cho luồng tìm kiếm pháp luật nhanh mà vẫn đúng](../../writeups/01-hieuluat-retrieval-optimization.vi.md)

Mục 6 của writeup đó đáng đọc. Hóa ra reranker làm tăng thêm 384 ms mà không cải thiện được gì.
Phần việc có ích là xác định kết quả đó thực sự quy trách nhiệm cho thành phần nào.

## Công nghệ

Python. PostgreSQL với pgvector. Embedding bge-m3 trên GPU. Một reranker cross encoder
(bge-reranker-v2-m3). Một pipeline chia giai đoạn, trong đó giai đoạn nào cũng chạy lại được. Các
eval set đã gán nhãn.

## Những gì mang sang được

Bốn điều ở đây không phụ thuộc vào code riêng tư, và tôi sẽ làm lại đúng như vậy ở bất kỳ chỗ nào.

Chọn điểm vận hành của một index xấp xỉ theo cam kết về tính đúng đắn, không theo mục tiêu latency.
Tách embedding thành việc chạy hàng loạt và việc chạy trực tuyến, vì hai việc nghẽn ở chỗ khác nhau.
Khi một con số chất lượng không chịu nhúc nhích, hãy nghi ngờ eval set trước khi tin vào kết quả. Và
khi một thành phần tốn 384 ms mà không mang lại gì đo được, hãy bỏ nó ra, nhưng ghi lại phép đo có
thể đưa nó trở lại. Phương pháp đằng sau tất cả những điều này nằm trong
[Bài viết 03](../../writeups/03-reproducible-benchmarking.vi.md).
