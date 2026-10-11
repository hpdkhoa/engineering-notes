[English](01-hieuluat-retrieval-optimization.md) · **Tiếng Việt**

# Làm cho luồng tìm kiếm pháp luật nhanh mà vẫn đúng

### Vector index, rerank và embedding FP16, cùng các đánh đổi đã đo

> **Bối cảnh:** HieuLuat từng là một hệ thống hỏi đáp pháp luật Việt Nam. Hệ thống đã ngừng phát
> triển sau khi công ty được mua lại, còn code, corpus và prompt vẫn riêng tư. Bài viết này ở lại
> như một bản ghi về phương pháp. **Nội dung bài:** cách tôi làm cho luồng tìm kiếm của nó nhanh
> hơn mà không làm nó kém tin cậy đi. Một câu trả lời sai đến nhanh thì vẫn là câu mà luật sư sẽ
> nhắc lại với khách hàng. Bài này có các phép đo nhưng không có code.

---

## 0. Cấu hình máy đo

Một GPU phổ thông, NVIDIA RTX 4060 Ti 16 GB. Tôi đo các dòng ở mục 5 vào tháng 8 năm 2026 bằng
bench retrieval riêng của HieuLuat, với một bộ đánh giá cố định đã gán nhãn. Code của bench là
riêng tư, và từ đó tôi chưa chạy lại.

## 1. Hiện trạng ban đầu

Luồng tìm kiếm có ba phần dùng GPU hoặc database nhiều: một embedder (bge-m3), một phép tìm kiếm
cosine trên pgvector, và một reranker cross encoder.

Cả ba đều chạy được. Chưa ai tinh chỉnh phần nào.

1. Tìm kiếm vector không có index. Postgres tính khoảng cách tới từng dòng, rồi sắp xếp.
   Với vài nghìn chunk thì không sao. Khi corpus lớn dần, nó chậm đi.
2. Reranker đang tắt. Luồng tìm kiếm không dùng tới thành phần chấm độ liên quan tốt nhất.
3. Embedder chạy ở độ chính xác đầy đủ. Nó không có đường chạy FP16, nên nó dùng nhiều băng thông
   bộ nhớ hơn mức cần.

## 2. Bước 1: bổ sung vector index đúng nghĩa

Đây là thay đổi rẻ nhất và mang lại lợi ích lớn nhất. Tôi thay phép quét toàn bộ bằng một index
tìm láng giềng gần nhất xấp xỉ. pgvector có hai lựa chọn: IVFFlat, gom các vector thành các list,
và HNSW, dựng một graph. Cả hai đều thay phép quét toàn bộ bằng một phép tra cứu mở rộng được.

Rủi ro nằm ở chữ xấp xỉ. Các index này có thể bỏ sót láng giềng gần nhất thật sự. Trong đa số
sản phẩm, đó là một mất mát nhỏ về chất lượng. Trong một sản phẩm pháp luật thì không. HieuLuat
cam kết sẽ nói "không có thông tin" khi không tìm được câu trả lời. Nếu index bỏ mất chunk chứa câu
trả lời, hệ thống sẽ nói "không có thông tin" trong khi câu trả lời có tồn tại. Đó là một lỗi về
tính đúng.

Vì vậy phép thay thế này có cái giá của nó. Bạn đánh đổi recall lấy latency, và núm vặn là `probes`
trên IVFFlat hoặc `ef_search` trên HNSW.

Tôi đo latency của truy vấn khi corpus lớn dần, cho quét toàn bộ, IVFFlat và HNSW. Sau đó tôi đo
recall at k so với latency khi vặn núm. Đường cong thứ hai mới là đường hữu ích. Nó cho thấy bao
nhiêu latency đổi được bao nhiêu recall. Nhờ vậy tôi chọn được điểm vận hành theo ngưỡng về tính
đúng, thay vì đoán.

Tôi cần điểm mà recall vẫn đủ cao để giữ lời cam kết, rồi lấy latency thấp nhất có được tại điểm
đó.

## 3. Bước 2: retrieval diện rộng, rồi rerank

Khi đã có index, retrieval trở nên đủ rẻ để lấy một tập ứng viên lớn hơn và chấm điểm lại. Cross
encoder chấm điểm từng cặp câu hỏi và chunk, rồi giữ lại vài cặp tốt nhất.

Đây là một mẫu hai giai đoạn phổ biến. Nó thường cải thiện mức độ câu trả lời bám vào nguồn. Với
công việc pháp lý, đó là thước đo có ý nghĩa.

Nó cũng tạo ra một bài toán batching trên GPU đáng giải cho đúng. Reranker nên chấm điểm toàn bộ
tập ứng viên trong một forward pass FP16 theo batch, thay vì trong một vòng lặp Python.

Cái giá là latency. Lấy nhiều hơn rồi rerank thì tốn thời gian. Vì vậy kết quả cần báo cáo có ba
trục: recall, chất lượng câu trả lời, và số mili giây tăng thêm.

## 4. Bước 3: embedding FP16

Chạy bge-m3 ở half precision giảm khoảng một nửa bộ nhớ cần dùng và băng thông sử dụng. Trên một
GPU hiện đại, nó cũng tăng tốc forward pass. Với mục đích này, mất mát chất lượng là không đáng kể.

Ở đây có hai công việc khác nhau, và chúng có nút thắt khác nhau.

- Với ingest hàng loạt, khi tôi embed lại toàn bộ corpus, thông lượng là giới hạn. Batch lớn và
  FP16 giúp nhiều.
- Với truy vấn online, khi tôi embed một câu hỏi, giới hạn là latency và chi phí cố định. Batch
  size gần như không ảnh hưởng. Giữ model luôn nạp sẵn quan trọng hơn.

Dùng một batch size cho cả hai công việc là lỗi thường gặp. Tôi đo chúng riêng. Tôi đo chênh lệch
thông lượng giữa FP32 và FP16, và chạy một phép quét batch size. Phép quét cho thấy băng thông bộ
nhớ giới hạn embedder, đúng như kỳ vọng.

## 5. Kết quả đo

<!--measured:hieuluat-->
### Kết quả đo

**Vector index: recall vs latency**

| index | recall at 10 | p50 latency ms | p95 latency ms |
|---|---|---|---|
| sequential scan | 0.75 | 6.4 | 6.9 |
| sequential scan, FP32 embeddings | 0.75 | 6.4 | 7.6 |
| IVFFlat (lists=100) | 0.7 | 0.8 | 0.9 |
| IVFFlat (lists=100, probes=10) | 0.75 | 1.0 | 1.3 |
| HNSW (m=16) | 0.75 | 0.9 | 1.3 |

*Measured 2026-08, fixed evaluation set.*

**Two-stage rerank: quality vs added latency**

| config | answer quality pct | added latency ms |
|---|---|---|
| retrieve only (k=10) | 75.0 | 0 |
| retrieve k=50 + cross-encoder rerank | 75.0 | 383.6 |

*Measured 2026-08, fixed evaluation set.*

**Embedding precision: throughput & VRAM**

| precision | docs per sec bulk | vram gb |
|---|---|---|
| FP16 | 1414.5 | n/a |
| FP32 | 490.5 | n/a |

*Measured 2026-08, fixed evaluation set.*

<!--/measured-->

### Diễn giải số liệu

| Thay đổi | Công sức | Tác động | Những gì tôi đã đo |
|---|---|---|---|
| Vector index (IVFFlat hoặc HNSW) | Thấp | Tìm kiếm mở rộng được khi corpus lớn dần | Latency theo kích thước corpus, recall at k so với latency |
| Retrieval diện rộng, rồi rerank | Trung bình | Câu trả lời bám nguồn tốt hơn | Recall, chất lượng câu trả lời, latency tăng thêm |
| Embedding FP16 | Thấp | Embedding nhanh hơn, ít VRAM hơn | Thông lượng FP32 so với FP16, quét batch size |

Index đã tinh chỉnh đạt recall bằng phép quét vét cạn, với khoảng một phần sáu latency trung vị
của phép quét đó. Reranker thêm 384 ms và không thay đổi chất lượng câu trả lời chút nào. Khi
embedding corpus hàng loạt, FP16 nhanh hơn FP32 khoảng 2.9 lần. Cột VRAM ghi n/a vì harness không
lấy mẫu giá trị này, không phải vì nó bằng không. Mục 6 giải thích hai nhận xét đầu.

## 6. Trần recall, và vì sao rerank vô hiệu

Một kết quả trong bảng đó trông như một thất bại. Tôi mất một lúc mới tìm ra nó quy lỗi cho thành
phần nào.

Recall at 10 là 0.75 với phép quét toàn bộ. Phép quét toàn bộ là vét cạn. Nó so câu hỏi với từng
dòng, nên trong đó không có phép xấp xỉ nào làm mất recall. Nghĩa là 0.75 hoàn toàn không phải một
kết quả về index. Đó là trần của những gì embedding model này tìm được với k bằng 10 trên bộ đánh
giá này. Khoảng một phần tư số chunk đúng không nằm trong top mười, với bất kỳ index nào.

Đọc theo mức trần đó, phần việc về index đã làm đúng những gì nó cần làm. HNSW và IVFFlat đã tinh
chỉnh đều trả về 0.75, bằng phép quét vét cạn, trong khi cắt latency trung vị từ 6.4 ms xuống
khoảng 1 ms. IVFFlat chưa tinh chỉnh ở mức 0.70. Đó là cái giá của việc để `probes` ở giá trị mặc
định, và là lý do bước tinh chỉnh không phải tùy chọn.

Reranker cho kết quả âm tính. Lấy 50 ứng viên rồi chấm điểm lại chúng thêm 384 ms và không thay đổi
chất lượng câu trả lời chút nào.

Điều đó suy ra từ mức trần ở trên. Reranker chỉ sắp xếp lại các ứng viên mà retrieval đưa cho nó.
Nếu retrieval không bao giờ trả về chunk đúng, chấm điểm lại bao nhiêu cũng không tạo ra được nó.

Tôi chưa loại trừ được một nguyên nhân thứ hai. Một mức 0.75 phẳng trên mọi cấu hình cũng là hình
dạng của một bộ đánh giá hỏng. Phép đo phân biệt được hai trường hợp là recall at 50, tức tập ứng
viên mà reranker thực sự nhìn thấy.

- Nếu recall at 50 cũng quanh 0.75, các lần bỏ sót là bỏ sót retrieval thật. Khi đó cách sửa nằm ở
  phía trước cả index lẫn reranker: chia chunk tốt hơn, tìm kiếm lai giữa keyword và vector, hoặc
  một embedding model tốt hơn cho văn bản pháp luật tiếng Việt.
- Nếu recall at 50 cao hơn nhiều, các ứng viên đã có ở đó và reranker không đẩy được chúng lên. Đó
  là vấn đề của reranker, và là vấn đề dễ hơn.

Không ai đo con số đó trước khi sản phẩm đổi chủ, nên nhận định của tôi vẫn hẹp. Index không phải
nút thắt, và reranker chưa xứng đáng với 384 ms của nó. Vì vậy nó ra khỏi đường trả lời mặc định.
Nó ở ngoài cho tới khi có người đo recall at 50.

## 7. Hướng phát triển

Hướng mở rộng sâu nhất là một CUDA kernel viết tay cho một phần của đường chấm điểm. Nó sẽ gộp bước
chuẩn hóa và bước tích vô hướng trên tập ứng viên. Tôi sẽ profile nó bằng Nsight so với phiên bản
NumPy và phiên bản pgvector. Đó là khác biệt giữa gọi một thư viện GPU và tự viết kernel. Code của
HieuLuat là riêng tư, nên phần việc đó giờ diễn ra trong gen-system. Đường retrieval của gen-system
có cùng dạng chấm điểm cosine. Kế hoạch nằm trong
[writeup về inference](02-gen-system-inference-optimization.vi.md).

Đường chấm điểm chiếm dưới 1 ms trong một request mất khoảng 385 ms khi bật reranker. Một kernel ở
đó chứng minh năng lực. Nó sẽ không làm request nhanh lên. Nên tôi nói điều đó ngay từ đầu, đưa ra
roofline dự đoán kết quả, rồi vẫn cứ đo.

## 8. Những nguyên tắc tôi giữ lại

Nếu làm lại, tôi vẫn chọn điểm vận hành của index và tách phần việc embedding theo đúng cách đó.
Không có gì thông minh ở đây. Cả hai đều là thứ người ta bỏ qua khi đang vội.

Mục 6 mới là phần tôi còn nghĩ tới. Kết quả rerank ra âm tính, còn con số recall thì phẳng tới mức
đáng ngượng. Tìm ra con số phẳng đó quy lỗi cho thành phần nào, rồi gọi tên đúng một phép đo phân
định được, tốn thời gian hơn toàn bộ phần tinh chỉnh.

*Phương pháp nằm trong [benchmarking tái lập được](03-reproducible-benchmarking.vi.md). Giá trị tuyệt đối phụ thuộc vào GPU. Hình dạng của mỗi đánh đổi thì vẫn đúng trên card khác.*
