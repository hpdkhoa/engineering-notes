[English](README.md) · **Tiếng Việt**

# gen-system: hiểu code và sinh code chạy cục bộ

> Mô hình AI là một hộp đen. gen-system ghi lại từng giả định của mô hình về code của bạn,
> đối chiếu từng giả định với một graph deterministic dựng từ AST, và cho phép bạn sửa bất kỳ
> giả định nào. Sau đó nó kiểm chứng đầu ra đã sinh từ bên ngoài. Toàn bộ chạy trên máy của
> chính bạn. Tôi đang chuẩn bị mã nguồn để phát hành theo giấy phép Apache-2.0 tại
> [github.com/hpdkhoa/gen-system](https://github.com/hpdkhoa/gen-system); repo sẽ mở cùng lúc
> phát hành. Trang này trình bày kiến trúc và lý do đằng sau.

---

## Tóm lược

- **Lịch sử:** tôi tự xây dựng một mình từ tháng 11 năm 2025. Apache-2.0, đang chuẩn bị phát hành.
- **Công cụ:** Go. 266 tệp nguồn với 49.079 dòng, cùng 79 tệp test với 15.197 dòng và
  598 hàm test, trong 54 package. Harness benchmark có thêm 1.155 dòng Python và 3.308
  dòng shell. Đếm ngày 2026-09-11 tại commit `cfb0bff2`. Số dòng nguồn không tính code test và
  code sinh tự động.
- **Ngôn ngữ đọc được:** Go, COBOL kèm copybook, CA Gen, Java, TypeScript, Python. Phân giải symbol
  chính xác, call graph, control flow graph
- **Suy luận:** các mô hình open weight chạy qua Ollama trên một card RTX 4060 Ti 16 GB. `qwen3:14b`
  lập kế hoạch và `qwen2.5-coder:14b` viết code
- **Cổng chất lượng:** 13 bộ benchmark, baseline đóng băng, và các lần chạy lặp lại được ở temperature 0
  với seed cố định. Mỗi campaign kết thúc bằng một manifest và một attestation.

Số liệu tốc độ và VRAM nằm trong [writeup về inference](../../writeups/02-gen-system-inference-optimization.vi.md).
Writeup đó hiển thị chúng từ [các lần chạy đã đo](../../benchmarks/results/measured.json). Trang này
không lặp lại chúng, vì một con số sao chép sẽ lỗi thời ngay lần đầu bạn chạy lại bất cứ thứ gì.

## Nguyên lý

Mô hình AI là một hộp đen. Bạn không thấy được nó giả định điều gì về code của bạn. Bạn chỉ biết
khi đầu ra sai, và đó là thời điểm tốn kém nhất để biết.

Nên gen-system làm ba việc. Việc thứ ba là việc người ta hay bỏ qua.

**Ghi lại các giả định.** Nó dựng một graph deterministic từ AST: symbol, cạnh gọi hàm,
luồng điều khiển và tác động. Từ graph đó, với mỗi routine, nó liệt kê các đầu vào, các lời gọi
routine đó thực hiện, dữ liệu routine đó ghi, và hành động mà tên routine gợi ý. Nó gọi mỗi dòng
như vậy là một belief. Một mô hình cục bộ có thể thêm các claim. gen-system đối chiếu mọi claim
với graph, đánh dấu claim nào mâu thuẫn với những gì parser đã thấy, và không bao giờ dùng claim
đã đánh dấu. Bạn có thể sửa bất kỳ dòng nào. Chỉ những dòng con người đã xác minh mới định hướng
việc sinh code.

**Neo mô hình vào graph, không vào văn bản.** Ngữ cảnh cho mô hình lấy từ graph: bản tóm tắt
kiến trúc, các routine liên quan, các belief đã xác minh. Đây là graph RAG dựng từ AST, không
phải từ embedding của các đoạn văn bản.

**Kiểm chứng từ ngoài hộp đen.** gen-system biên dịch riêng từng operation đã sinh, rồi build
và test cả cây, rồi đọc lại bằng chính công cụ deterministic đã dựng graph. Bước cuối này bắt được những gì trình biên dịch không bắt được: lời gọi chưa phân giải, operation mồ
côi, một operation tên là đọc nhưng lại ghi. Phép kiểm tra phải đến từ thứ không dùng chung giả định
với mô hình. Nếu không, đó chỉ là mô hình tự xác nhận chính mình.

Nơi thử thách là code legacy. COBOL kèm copybook và CA Gen nằm cạnh Go, Java,
TypeScript và Python. Legacy là nơi không ai nói được hệ thống làm gì. Đó cũng là nơi một câu
trả lời sai tốn kém nhất.

Một bài báo tháng 1 năm 2026, Reliable Graph-RAG for Codebases (arXiv 2601.08773), thử điều này trên
Java và thấy đúng như vậy: graph AST deterministic neo mô hình chắc hơn và rẻ hơn graph do
LLM dựng hoặc vector search. Bản đầu tiên của tôi chạy trước bài báo đó hai tháng, nên đọc nó thấy
yên tâm. gen-system bao phủ sáu ngôn ngữ và đi tiếp qua retrieval, sang belief, sinh code và bước
kiểm chứng.

Nó cũng chạy cục bộ, nên không có code nào rời khỏi máy, và cùng một đầu vào cho ra cùng một đầu ra.

## Kiến trúc

**Lớp phân tích.** Phân giải symbol chính xác ngang trình biên dịch, call graph và control flow graph.
Nó làm việc trên cấu trúc mà trình biên dịch nhìn thấy, không phải trên code như văn bản.

**Lớp sinh code.** Các mô hình cục bộ qua Ollama, với mô hình riêng cho lập kế hoạch và cho viết code,
chạy ở temperature 0 với seed cố định. Ngoài ra còn một nhánh template deterministic không cần mô
hình nào.

**Lớp kiểm chứng.** Các project đã sinh phải build được và qua test của chúng. Sau đó nửa phân
tích đọc lại code đã sinh và báo cáo những gì nó tìm thấy. Bước này bắt được những vấn đề mà trình
biên dịch không thấy.

**Harness benchmark.** Baseline đóng băng và regression gate. Một thay đổi parser làm giảm recall
phân giải trên baseline COBOL đã commit sẽ làm gate thất bại ngay lập tức, thay vì lộ ra về sau.

**Điều phối.** Retry, ràng buộc đầu ra có cấu trúc, và keep alive cho mô hình để việc nạp lại mô
hình không rơi vào giữa một lần chạy.

## Quyết định thiết kế và căn cứ

**Ưu tiên chạy cục bộ.** Tôi chọn quyền riêng tư và khả năng lặp lại, thay vì sự tiện lợi của
một API dựng sẵn trên cloud. Toàn bộ pipeline chạy trên phần cứng của bạn.

**Determinism.** Temperature 0 và seed cố định. Thiếu nó, một benchmark đo nhiễu lấy mẫu nhiều ngang
với đo hệ thống.

**Hai mô hình chuyên biệt thay vì một mô hình tổng quát.** Lập kế hoạch và viết code là hai việc
khác nhau, và chuyên biệt hóa giúp cả hai tốt hơn. Cái giá là một vấn đề thật: hai mô hình tranh
nhau 16 GB. Hệ thống xử lý bằng keep alive và tinh chỉnh timeout, và writeup đo cái giá đó.

**Một thước đo chất lượng khách quan, và một lần sửa nó.** Tiêu chuẩn là code có build được và qua
test hay không. Tiêu chuẩn này tốt hơn một thước đo gián tiếp dựa trên perplexity. Nhưng phiên bản
đầu của thước đo đó vô dụng. Khi một operation do mô hình viết không qua compile gate, gate thay nó
bằng một stub `not implemented` tường minh, và stub thì biên dịch được. Vì vậy tỷ lệ qua là 100
phần trăm ngay từ cách xây dựng.

Hiện nay harness đo lượng logic thật còn sống sót qua gate thay vì rơi về stub, cùng số lần sửa. Lần
sửa đó đáng giá hơn con số mà nó thay thế.

**Quy ước của team thành một hợp đồng có kiểm tra.** Một team có thể đưa cho bộ sinh code một hồ
sơ phong cách: cách đặt tên, bố cục thư mục, các pattern bắt buộc và bị cấm, giới hạn kích thước,
kiểu vòng lặp, import. Bạn viết hồ sơ bằng tay, hoặc `gen style derive` đo nó từ một repo có sẵn
thông qua symbol graph và giữ số lượng bằng chứng cạnh mỗi quy tắc suy ra. Các quy tắc đi vào mọi
prompt mà mô hình coder nhận. Sau khi sinh, parser kiểm tra chính các quy tắc đó trên đầu ra, không
có mô hình nào tham gia. Một operation biên dịch được nhưng vi phạm quy tắc sẽ quay lại mô hình, kèm
tên quy tắc. Phong cách không bao giờ biến logic thành stub. Chỉ compile gate làm điều đó.

**Một chứng nhận cho mỗi campaign.** Mỗi lần chạy benchmark kết thúc bằng một attestation và một
manifest. Attestation ghi những gì đã chạy, trên commit nào và máy nào, những lần chạy nào nó loại
vì chưa đo và lý do, và những gì đã không chạy. Manifest liệt kê mọi tệp thô cùng hash của
nó. Mọi con số trong writeup đều truy ngược được về các tệp đó.

## Kết quả đo

Phần tinh chỉnh inference bao gồm offload layer lên GPU, streaming đầu ra, quantization xem như
một biến cần đo, và vấn đề VRAM khi chạy hai mô hình:

→ [Tinh chỉnh inference LLM cục bộ cho một công cụ xử lý code](../../writeups/02-gen-system-inference-optimization.vi.md)

Phương pháp benchmark đứng sau phần đó, với baseline đóng băng và gate, là một writeup riêng:

→ [Benchmark tái lập được và regression gate](../../writeups/03-reproducible-benchmarking.vi.md)

Bản thân các bảng số liệu, kèm nguồn gốc của chúng, nằm trong [benchmarks/](../../benchmarks/README.vi.md).

## Nền tảng kỹ thuật

Go. LLM cục bộ qua Ollama, với một mô hình planner và một mô hình coder. Phân tích chính xác ngang
trình biên dịch, gồm phân giải symbol, call graph và control flow graph. Sinh code deterministic.
Một harness benchmark có regression gate.

## Vị trí mã nguồn

Tôi đang chuẩn bị mã nguồn để phát hành theo giấy phép Apache-2.0 tại
[github.com/hpdkhoa/gen-system](https://github.com/hpdkhoa/gen-system). Repo giữ private cho đến khi
phát hành và mở cùng lúc phát hành. Repo chứa sáu parser, lớp belief, pipeline sinh code, các
driver benchmark trong `bench/`, kết quả của campaign 2026-09-09 kèm manifest và attestation, tài
liệu kỹ thuật trong `docs/`, và bộ test.

Writeup về inference mô tả hai lỗi determinism tôi tìm thấy trong quá trình này, cùng với các
test thất bại trên code cũ. Chúng nằm trong lịch sử repo, không chỉ trong writeup.
