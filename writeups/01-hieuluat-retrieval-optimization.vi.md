[English](01-hieuluat-retrieval-optimization.md) · **Tiếng Việt**

# Làm cho luồng tìm kiếm pháp luật nhanh mà vẫn đúng

### Vector index, rerank và embedding FP16, cùng các đánh đổi đã đo

> **Bối cảnh:** HieuLuat là một hệ thống hỏi đáp pháp luật Việt Nam. Xem
> [trang dự án](../projects/hieuluat/README.vi.md). Đây là một sản phẩm thương mại đang được chuyển
> giao quyền sở hữu, nên code, corpus và prompt là riêng tư. **Nội dung bài:** cách tôi làm cho
> > luồng tìm kiếm của nó nhanh hơn mà không làm nó kém tin cậy đi. Một câu trả lời sai đến nhanh
> thì vẫn là câu mà luật sư sẽ nhắc lại với khách hàng. Các phép đo nằm bên dưới. Code thì không.

---

## 0. Cấu hình máy đo

Một GPU phổ thông. Tôi đo các dòng ở mục 5 vào tháng 8 năm 2026 bằng benchmark retrieval
riêng của HieuLuat, trên một NVIDIA RTX 4060 Ti 16 GB, với một bộ đánh giá cố định đã gán nhãn.
Kết quả được ghi vào
[`benchmarks/results/measured.json`](../benchmarks/results/measured.json), mỗi cấu hình một nhãn.
Bản thân harness và commit của nó nằm trong repository riêng tư. Vì vậy các dòng này chỉ mang theo
ngày đo, bộ đánh giá và GPU, không có gì hơn. Từ đó đến nay chúng chưa được chạy lại, và writeup
này không giả vờ là đã chạy lại. Chỗ nào văn bản bên dưới đọc một con số từ bảng, thì lấy bảng làm
chuẩn.

## 1. Hiện trạng ban đầu

Luồng tìm kiếm có ba phần dùng GPU hoặc database nhiều: một embedder (bge-m3), một phép tìm kiếm
cosine trên pgvector, và một reranker cross encoder.

Cả ba đều chạy được. Không phần nào được tinh chỉnh. Có ba vấn đề nổi bật:

1. **Tìm kiếm vector không có index.** Postgres tính khoảng cách tới từng dòng, rồi sắp xếp.
   Với vài nghìn chunk thì không sao. Khi corpus lớn dần, nó chậm đi.
2. **Reranker đang tắt.** Thành phần chấm độ liên quan tốt nhất thì lại nằm im.
3. **Embedder chạy ở độ chính xác đầy đủ.** Không có đường chạy FP16, nên nó dùng nhiều băng thông
   bộ nhớ hơn mức cần.

## 2. Bước 1: bổ sung vector index đúng nghĩa

Đây là thay đổi rẻ nhất và mang lại lợi ích lớn nhất. Tôi thay phép quét toàn bộ bằng một index
tìm láng giềng gần nhất xấp xỉ. pgvector có hai lựa chọn: IVFFlat, gom các vector thành các list,
và HNSW, dựng một graph. Cả hai đều thay phép quét toàn bộ bằng một phép tra cứu mở rộng được.

**Vấn đề nằm ở chữ xấp xỉ.** Các index này có thể bỏ sót láng giềng gần nhất thật sự. Trong đa số
sản phẩm, đó là một mất mát nhỏ về chất lượng. Trong một sản phẩm pháp luật thì không. HieuLuat
cam kết sẽ nói "không có thông tin" khi không tìm được câu trả lời. Nếu index bỏ mất chunk chứa câu
trả lời, hệ thống sẽ nói "không có thông tin" trong khi câu trả lời có tồn tại. Đó là một lỗi về
tính đúng, không phải một chi tiết tinh chỉnh tốc độ.

Vì vậy đây không phải một phép thay thế miễn phí. Đây là một đánh đổi giữa recall và latency, và
thiết lập `probes` hoặc `ef_search` là núm vặn.

**Những gì tôi đã đo.** Latency của truy vấn khi corpus lớn dần, cho quét toàn bộ, IVFFlat và HNSW.
Sau đó là recall at k so với latency khi tôi vặn núm. Đường cong thứ hai mới là đường hữu ích. Nó
cho thấy bao nhiêu latency đổi được bao nhiêu recall. Nhờ vậy điểm vận hành được chọn theo ngưỡng
về tính đúng, thay vì đoán.

Mục tiêu chưa bao giờ là dùng index nhanh nhất. Mục tiêu là tìm điểm mà recall vẫn đủ cao để giữ
lời cam kết. Rồi lấy latency thấp nhất có được tại điểm đó.

## 3. Bước 2: retrieval diện rộng, rồi rerank

Khi đã có index, retrieval trở nên đủ rẻ để lấy một tập ứng viên lớn hơn và chấm điểm lại. Cross
encoder chấm điểm từng cặp câu hỏi và chunk, rồi giữ lại vài cặp tốt nhất.

Đây là một mẫu hai giai đoạn phổ biến. Nó thường cải thiện mức độ câu trả lời bám vào nguồn. Với
công việc pháp lý, đó là thước đo có ý nghĩa.

Nó cũng tạo ra một bài toán batching trên GPU đáng giải cho đúng. Reranker nên chấm điểm toàn bộ
tập ứng viên trong một forward pass FP16 theo batch, không phải trong một vòng lặp Python.

Cái giá là latency. Lấy nhiều hơn rồi rerank thì tốn thời gian. Vì vậy kết quả cần báo cáo có ba
trục: recall, chất lượng câu trả lời, và số mili giây tăng thêm.

## 4. Bước 3: embedding FP16

Chạy bge-m3 ở half precision giảm khoảng một nửa bộ nhớ cần dùng và băng thông sử dụng. Trên một
GPU hiện đại, nó cũng tăng tốc forward pass. Với mục đích này, mất mát chất lượng là không đáng kể.

Phần cần làm cho đúng là ở đây có hai công việc khác nhau, và chúng có nút thắt khác nhau:

- **Ingest hàng loạt**, khi embedding lại toàn bộ corpus, bị giới hạn bởi thông lượng. Batch lớn
  và FP16 giúp nhiều.
- **Truy vấn online**, khi embedding một câu hỏi, bị giới hạn bởi latency và chi phí cố định. Batch
  size gần như không ảnh hưởng. Giữ model luôn nạp sẵn quan trọng hơn.

Dùng một batch size cho cả hai công việc là lỗi thường gặp. Tôi đo chúng riêng: chênh lệch thông
lượng giữa FP32 và FP16, và một phép quét batch size. Phép quét cho thấy embedder bị giới hạn bởi
băng thông bộ nhớ, đúng như kỳ vọng.

## 5. Kết quả đo

<!--measured:hieuluat-->
### Bảng số liệu

*Dựng từ `benchmarks/results/measured.json`. Mọi con số dưới đây đến từ harness của chính dự án, trên máy được mô tả ở mục 0.*

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

Ba nhận xét. Index đã tinh chỉnh đạt recall bằng phép quét vét cạn, với khoảng một phần sáu latency
trung vị của phép quét đó. Reranker thêm 384 ms và không thay đổi chất lượng câu trả lời chút nào.
Khi embedding corpus hàng loạt, FP16 nhanh hơn FP32 khoảng 2.9 lần. Cột VRAM ghi n/a vì harness
không lấy mẫu giá trị này, không phải vì nó bằng không. Nhận xét thứ nhất và thứ hai là nội dung
của mục 6.

## 6. Trần recall, và vì sao rerank vô hiệu

Một kết quả trong bảng đó trông như một thất bại. Nó đáng đọc kỹ, vì phần thú vị là nó thực sự quy
lỗi cho thành phần nào.

Recall at 10 là 0.75 với phép quét toàn bộ. **Phép quét toàn bộ là vét cạn.** Nó so câu hỏi với
từng dòng, nên trong đó không có phép xấp xỉ nào làm mất recall. Nghĩa là 0.75 hoàn toàn không phải
một kết quả về index. Đó là trần của những gì embedding model này tìm được với k bằng 10 trên bộ
đánh giá này. Khoảng một phần tư số chunk đúng không nằm trong top mười, với bất kỳ index nào.

Đọc theo mức trần đó, phần việc về index đã làm đúng những gì nó cần làm. HNSW và IVFFlat đã tinh
chỉnh đều trả về 0.75, bằng phép quét vét cạn, trong khi cắt latency trung vị từ 6.4 ms xuống
khoảng 1 ms. IVFFlat chưa tinh chỉnh ở mức 0.70. Đó là cái giá thật của việc để `probes` ở giá trị
mặc định, và là lý do bước tinh chỉnh không phải tùy chọn. Vậy index mang lại mức giảm latency
khoảng sáu lần mà không tốn recall. Nó không "đứng yên".

**Reranker là một chuyện khác, và là một kết quả âm tính thật sự.** Lấy 50 ứng viên rồi chấm điểm
lại chúng thêm 384 ms và không thay đổi chất lượng câu trả lời chút nào.

Điều đó suy ra từ mức trần ở trên. Reranker sắp xếp lại các ứng viên được đưa cho nó. Nó không thể
tìm ra một chunk mà retrieval chưa bao giờ trả về. Nếu chunk đúng không có trong tập ứng viên, chấm
điểm lại bao nhiêu cũng không đưa nó trở lại.

**Điều tôi chưa tách bạch.** Một mức 0.75 phẳng trên mọi cấu hình cũng là hình dạng của một bộ đánh
giá bị hỏng. Phép đo phân biệt được hai trường hợp là recall at 50, tức tập ứng viên mà reranker
thực sự nhìn thấy.

- Nếu recall at 50 cũng quanh 0.75, các lần bỏ sót là bỏ sót retrieval thật. Khi đó cách sửa nằm ở
  phía trước cả index lẫn reranker: chia chunk tốt hơn, tìm kiếm lai giữa keyword và vector, hoặc
  một embedding model tốt hơn cho văn bản pháp luật tiếng Việt.
- Nếu recall at 50 cao hơn nhiều, các ứng viên đã có ở đó và reranker không đẩy được chúng lên. Đó
  là vấn đề của reranker, và là vấn đề dễ hơn.

Không ai đo con số đó trước khi sản phẩm đổi chủ, nên nhận định trung thực vẫn là nhận định hẹp.
Index không phải nút thắt, và reranker chưa xứng đáng với 384 ms của nó. Đường trả lời mặc định
không nên trả chi phí đó. Bỏ một thành phần tốn chừng đó mà không mang lại gì đo được là làm kỹ
thuật tốt. Phép đo có thể đưa nó trở lại đã được nêu ở trên.

## 7. Hướng phát triển

Hướng mở rộng sâu nhất là một CUDA kernel viết tay cho một phần của đường chấm điểm. Nó sẽ gộp bước
chuẩn hóa và bước tích vô hướng trên tập ứng viên, và được profile bằng Nsight so với phiên bản
NumPy và phiên bản pgvector. Đó là khác biệt giữa gọi một thư viện GPU và tự viết kernel. Vì code của
HieuLuat là riêng tư, phần việc đó giờ diễn ra trong gen-system. Đường retrieval của gen-system có
cùng dạng chấm điểm cosine; kế hoạch nằm trong
[writeup về inference](02-gen-system-inference-optimization.vi.md).

Lưu ý này phải nói trước, vì nó là toàn bộ hình dạng của việc này. Đường chấm điểm chiếm dưới 1 ms
trong một request mất khoảng 385 ms khi bật reranker. Một kernel ở đó chứng minh năng lực. Nó sẽ
không làm request nhanh lên. Nên tôi nói thẳng ngay từ đầu, đưa ra roofline dự đoán kết quả, rồi vẫn
cứ đo.

## 8. Những nguyên tắc tôi giữ lại

Tôi chọn điểm vận hành của index theo cam kết an toàn chứ không theo mục tiêu latency, và tách phần
việc embedding thành hai công việc nghẽn ở chỗ khác nhau. Không có gì thông minh ở đây. Cả hai đều
là thứ người ta bỏ qua khi đang vội.

Mục 6 mới là phần tôi còn nghĩ tới. Kết quả rerank ra âm tính, còn con số recall thì phẳng tới mức
đáng ngượng. Tìm ra con số phẳng đó quy lỗi cho thành phần nào, rồi gọi tên đúng một phép đo phân
định được, tốn thời gian hơn toàn bộ phần tinh chỉnh.

*Các phép đo được thực hiện trước và sau, với các bộ đánh giá cố định, trên máy ở mục 0. Phương
pháp nằm trong [benchmarking tái lập được](03-reproducible-benchmarking.vi.md). Giá trị tuyệt đối phụ thuộc vào GPU. Hình dạng của mỗi đánh đổi thì vẫn đúng trên card khác.*
