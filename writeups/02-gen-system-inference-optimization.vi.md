[English](02-gen-system-inference-optimization.md) · **Tiếng Việt**

# Tinh chỉnh inference LLM cục bộ cho một công cụ xử lý code

### GPU offload, streaming, quantization, và hai model dùng chung một card phổ thông

> **Bối cảnh:** gen-system làm cho niềm tin của một model AI về code trở nên nhìn thấy được và kiểm
> tra được. Nó neo model vào một graph dựng từ AST, và kiểm chứng đầu ra từ bên ngoài. Xem
> [trang dự án](../projects/gen-system/README.vi.md). Mã nguồn đang được chuẩn bị để phát hành theo
> Apache-2.0. **Nội dung bài này:** tinh chỉnh tầng inference của nó. Phép kiểm tra chất lượng là
> khách quan: code sinh ra hoặc build được và qua test của nó, hoặc không. Mục 4 giải thích vì sao
> phiên bản dễ nghĩ tới nhất của phép kiểm tra đó vô dụng, và cái gì đã thay thế nó.

---

## 0. Cỗ máy

Một GPU phổ thông, chính là card trong máy bàn của tôi. Một NVIDIA RTX 4060 Ti 16 GB, chạy Ollama,
với một model planner và một model coder dùng chung card.

Trong production, `qwen3:14b` đảm nhận việc lập kế hoạch và `qwen2.5-coder:14b` đảm nhận việc viết
code. Nghiên cứu quantization dùng `deepseek-coder-v2:16b-lite-instruct` ở Q4_K_M, Q5_K_M và Q8_0.

Decoding là deterministic: temperature 0, seed 42, top_p 1. Có một test kiểm tra điều đó, và mục 6
chỉ ra chỗ việc ghim tham số không còn giữ được.

Harness ghi lại chính xác GPU, driver, các phiên bản runtime, commit và danh sách model vào
[ENVIRONMENT.md](../benchmarks/ENVIRONMENT.vi.md). Mỗi bảng ở mục 6 ghi kèm commit và ngày đo. Các
bảng đó được sinh ra từ
[`benchmarks/results/measured.json`](../benchmarks/results/measured.json). Các bảng là nguồn của mọi con số. Khi một bảng đổi, tôi viết lại phần chữ bên dưới nó.

## 1. Điểm xuất phát

Mọi lệnh inference đi qua một client duy nhất tới một runtime Ollama cục bộ. Bức tranh nhất quán.
Nó đúng, nó deterministic, và nó hoàn toàn chưa được tinh chỉnh.

- **Mỗi lệnh gọi đều chờ toàn bộ câu trả lời.** Client bị chặn cho tới khi sinh xong. Một lần sinh
  code dài phải chờ trọn thời gian trước khi token đầu tiên xuất hiện. Không bước nào phía sau có
  thể bắt đầu sớm.
- **Không có điều khiển GPU nào.** Tùy chọn của request đặt temperature, seed và top_p. Không có gì
  quy định cách GPU chạy model. Không có layer offload, không có kích thước context, không có kích
  thước batch. Runtime chạy theo giá trị mặc định.
- **Quantization bị cố định.** Tag của model mang một mức quant. Đó là một lựa chọn, chưa bao giờ là
  một phép đo.
- **Hai model dùng chung 16 GB.** Đây là lý do hệ thống cần keep alive và một timeout dài. Một lần
  nạp lại model có thể rơi vào giữa một lần chạy, và không có gì đo nó tốn bao nhiêu.

Tầng tính đúng đã vững. Tầng hiệu năng chưa được đụng tới, và tầng đó mới là công việc thực sự.

## 2. Bước 1: mở các điều khiển GPU

Mọi lưu lượng tới model đi qua một hàm duy nhất. Giờ ba thiết lập được đọc từ biến môi trường và
được gửi kèm mọi request:

| Biến | Nó điều khiển gì |
|---|---|
| `OLLAMA_NUM_GPU` | Số layer chạy trên GPU. Đây là đòn bẩy lớn nhất. Với hai model 14B trên 16 GB, việc các layer vừa GPU hay tràn sang CPU quyết định giữa nhanh và không dùng được. |
| `OLLAMA_NUM_CTX` | Kích thước cửa sổ context. KV cache tăng theo nó. Prompt ở đây lớn, nên thiết lập này đánh đổi VRAM lấy năng lực. |
| `OLLAMA_NUM_BATCH` | Kích thước batch khi xử lý prompt. Nó quyết định tốc độ prefill. |

Mỗi thiết lập bị bỏ khỏi request khi biến của nó chưa được đặt. Một máy không đặt biến nào sẽ gửi
đúng request như client cũ. Tính chất đó giữ cho phép đo trung thực. Lần chạy đã tinh chỉnh và lần
chạy chưa tinh chỉnh chỉ khác nhau ở thiết lập đang được thử.

Bench driver quét `OLLAMA_NUM_GPU` và lấy mẫu VRAM đỉnh ở mỗi bước.

## 3. Bước 2: stream đầu ra

Streaming được bật qua `OLLAMA_STREAM`. Bộ đọc tiêu thụ stream và ghép các mảnh lại thành một chuỗi.
Chuỗi đó giống hệt chuỗi mà đường buffered cũ trả về.

Điều này quan trọng hơn vẻ ngoài của nó. Mọi thứ phía sau nhận cùng một đầu vào trong cả hai trường
hợp: bước trích JSON, quy tắc thân hàm sinh ra phải trả về riêng lẻ, và bước kiểm tra determinism.
Tầng truyền tải không được phép thay đổi ý nghĩa. Một test khẳng định chỉ có một đầu ra duy nhất qua
năm response streaming giống hệt nhau.

Buffered vẫn là mặc định. Streaming phải bật chủ động cho tới khi phép đo cho thấy điều khác.

Những gì được đo là time to first token và tổng thời gian, khi bật và khi tắt streaming, trên cùng
một prompt, mỗi cấu hình ba lần chạy.

## 4. Bước 3: quantization, và thước đo hỏng nằm bên dưới

Ở đây quantization là một thí nghiệm, không phải một lựa chọn cố định. Cùng một model chạy ở Q4_K_M,
Q5_K_M và Q8_0 cho vai trò coder, với planner giữ cố định. Mỗi lần chạy đo tốc độ, VRAM và chất
lượng.

Trục chất lượng là chỗ việc này trở nên thú vị. Đó cũng là chỗ phiên bản đầu của writeup này đã
sai.

**Thước đo dễ nghĩ tới nhất không dùng được.** Kế hoạch là báo cáo tỷ lệ compile thành công. Code
sinh ra hoặc build được, hoặc không. Mọi lần chạy đều ra 100 phần trăm.

Đó không phải vì model hoàn hảo. Đó là **do chính cách thiết kế**. Khi một operation do model viết
không compile được, công cụ gửi nó lại cho model kèm lỗi build. Nếu vẫn lỗi, công cụ thay thân hàm
bằng một stub `not implemented` tường minh. Stub compile được. Service luôn build được.

Một thước đo không thể giảm thì không đo được gì. Một mức quantization làm hỏng nặng đầu ra vẫn đạt
100 phần trăm.

**Cái đã thay thế nó.** Phần đo đạc giờ đếm những gì thực sự thay đổi. Tất cả đến từ cùng đường code
mà production dùng:

| Thước đo | Nó bắt được gì |
|---|---|
| `ops_stubbed` và `stub_rate_pct` | Bao nhiêu logic do model viết không qua cổng compile và phải lùi về stub. Đây là tín hiệu chất lượng thực sự. |
| `op_repair_attempts` và `op_repair_successes` | Số vòng sửa ở cấp operation, tối đa 2 vòng trước khi dùng stub. Một mức quant yếu hơn lẽ ra sẽ cần nhiều vòng hơn. |
| `heal_attempts_total` và `heal_success` | Số vòng sửa ở cấp task, tối đa 3 vòng. |
| `go_test_pass` | Backend sinh ra có qua test của chính nó hay không, kể cả một test sẽ fail nếu một operation panic lúc runtime. |
| `verify_findings` | Những gì công cụ hiểu code của chính dự án tìm thấy khi đọc lại backend sinh ra: lời gọi chưa resolve được, operation mồ côi, operation đọc nhưng lại ghi. |
| `prompt_tokens` và `wall_s` | Chi phí cho mỗi lần chạy. |

Tỷ lệ compile thành công vẫn được báo cáo. Nó không còn là con số chính. Lý do nó vô dụng giờ được
ghi ra thay vì bị giấu đi.

Bộ task gồm năm ý tưởng ứng dụng cố định. Chúng được đóng băng và commit trước lần chạy đầu tiên,
nên không thể chỉnh chúng cho khớp với kết quả.

## 5. Bước 4: hai model, một card

Hai model tranh nhau 16 GB là một bài toán thiết kế thật, có nhiều hơn một lời giải tốt. Ba chiến
lược chạy trên cùng bộ task đã đóng băng:

| Chiến lược | Nó là gì | Nó tốn gì |
|---|---|---|
| A. Tuần tự với keep alive | Mặc định của production. Mỗi lúc chỉ một model nằm trong bộ nhớ. | Một lần nạp lại model khi đổi vai trò. Đo bằng chênh lệch thời gian nạp. |
| B. Cả hai cùng nằm trong bộ nhớ | Keep alive không bao giờ hết hạn, nên cả hai model lẽ ra đều được giữ nóng. | Khoảng trống VRAM, và tốc độ khi tranh chấp tài nguyên. Việc cả hai có vừa hay không tự nó là một kết quả, và mục 6 đưa ra câu trả lời. |
| C. Một model dùng chung | Model coder cũng lập kế hoạch, nên không bao giờ phải đổi model. | Chất lượng lập kế hoạch, thể hiện qua stub rate, số vòng sửa và các entity thừa. |

Có một điều cần làm rõ ở mọi nơi mô tả việc này. **Không có scheduler.** "Lập lịch tuần tự với keep
alive" nghĩa là keep alive có sẵn của Ollama, hai vai trò model, và phép đo chi phí của cách làm đó.
Không có dòng code lập lịch nào được viết. Nói khác đi sẽ không đứng vững khi ai đó đọc mã nguồn.

## 6. Kết quả

<!--measured:gen-->
### Kết quả đo

*Dựng từ `benchmarks/results/measured.json`. Mọi con số dưới đây đến từ harness của chính dự án, trên máy được mô tả ở mục 0.*

**GPU-layer offload: tokens/sec vs VRAM**

| gpu layers | tokens per sec | vram gb | n | tok s min | tok s max |
|---|---|---|---|---|---|
| 20 | 7.9 | 4.7 | 3 | n/a | n/a |
| 30 | 10.2 | 6.3 | 3 | n/a | n/a |
| 40 | 14.3 | 8.0 | 3 | n/a | n/a |
| default | 30.8 | 9.4 | 3 | n/a | n/a |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Streaming: time-to-first-token**

| config | ttft ms | total latency s | n | ttft min | ttft max |
|---|---|---|---|---|---|
| stream off (buffered) | 1883.7 | 1.88 | 3 | 1876.4 | 1897.5 |
| stream on (NDJSON) | 127.4 | 1.88 | 3 | 126.7 | 128.0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Quantization sweep: speed vs VRAM vs generation quality**

| quant | tokens per sec | vram gb | ops total | stub rate pct | op repair attempts | heal attempts | go test pass | n | tok s min | tok s max | runs not measured |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q4_K_M | 125.2 | 11.5 | 25.3 | 91.1 | 46.7 | 0.0 | 5.0 | 3 | 124.5 | 125.6 | 0 |
| Q5_K_M | 114.4 | 12.8 | 23.7 | 83.8 | 43.0 | 0.0 | 5.0 | 3 | 114.0 | 114.6 | 0 |
| Q8_0 | 41.3 | 15.3 | 24.0 | 76.7 | 40.0 | 3.0 | 4.7 | 3 | 41.0 | 41.5 | 0 |
| production | 30.7 | 9.6 | 3.0 | 44.4 | 2.7 | 0.0 | 5.0 | 3 | 30.7 | 30.7 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Two-model serving strategies**

| strategy | reload cost s | tokens per sec | ops total | stub rate pct | heal attempts | go test pass | n | runs not measured |
|---|---|---|---|---|---|---|---|---|
| A-sequential-keepalive | 1.98 | 30.7 | 3.0 | 0.0 | 0.0 | 5.0 | 3 | 0 |
| B-both-resident | 1.96 | 30.7 | 3.0 | 66.7 | 0.0 | 5.0 | 3 | 0 |
| C-single-shared | 1.97 | 30.7 | 3.0 | 0.0 | 0.0 | 5.0 | 3 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Understand benchmark: public repos at pinned commits**

| repo | files | parse errors | internal recall pct | call edges internal | cfgs total | cfgs with issue |
|---|---|---|---|---|---|---|
| cobolcraft | 268 | 0 | 100 | 298 | 330 | 0 |
| go-chi | 84 | 0 | 100 | 1212 | 411 | 0 |
| gorilla-mux | 17 | 0 | 100 | 274 | 158 | 0 |
| spf13-cobra | 36 | 0 | 100 | 984 | 403 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**SWE-bench Verified: localization recall (not a solve rate)**

| hops | file recall mean | hit rate pct | mean neighbourhood files | median neighbourhood files | n tasks |
|---|---|---|---|---|---|
| 0 | 0.615 | 63.3 | 201.933 | 92.5 | 60 |
| 1 | 0.615 | 63.3 | 262.5 | 177.5 | 60 |
| 2 | 0.674 | 70.0 | 464.8 | 421.5 | 60 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

**SWE-bench Verified: localization recall by repository**

| repo | hops | file recall mean | hit rate pct | seeds matched pct | n tasks |
|---|---|---|---|---|---|
| astropy/astropy | 2 | 0.716 | 77.3 | 100.0 | 22 |
| django/django | 2 | 0.649 | 65.8 | 92.1 | 38 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

**SWE-bench Verified: can the parsers read the repositories**

| repo | files parsed | parse errors | internal recall pct | call edges internal |
|---|---|---|---|---|
| astropy/astropy | 786 | 0 | 92.6 | 22851 |
| django/django | 2572 | 0 | 96.1 | 50596 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

<!--/measured-->

### Các con số nói gì

| Thay đổi | Tác động | Những gì được đo |
|---|---|---|
| Điều khiển GPU | Tốc độ và khả năng vừa trên một card | Tokens per second và VRAM đỉnh theo số layer được offload |
| Streaming | Time to first token thấp hơn | Time to first token và tổng thời gian, bật và tắt, ba lần chạy |
| Quantization | Tốc độ và VRAM đánh đổi với chất lượng | Tốc độ, VRAM, stub rate, số vòng sửa, test pass |
| Chiến lược hai model | Phục vụ mà không phải nạp lại model | Chi phí nạp lại, tốc độ, stub rate qua ba chiến lược |

Mọi bảng ở trên đến từ một campaign, chạy ngày 2026-09-09 ở một commit sạch, trong một thư mục kết
quả. Manifest và attestation nằm cạnh các file dữ liệu thô trong repo gen-system. Ba campaign trước
đó dẫn tới nó. Campaign đầu tiên chạy với working tree chưa sạch. Campaign thứ hai và thứ ba thực ra
là một lần chạy vắt qua nửa đêm và bị tách thành hai thư mục. Đó là cách một bug về ngày trong các
driver được phát hiện. Mỗi campaign đó tìm ra một điều mà các bảng giờ đã phản ánh. Có chín điều
đáng đọc ra từ các bảng.

**Thước đo chất lượng đã dịch chuyển.** Stub rate khác nhau ở mỗi mức quantization. Đó chính là mục
đích của việc thay tỷ lệ compile thành công, vốn luôn là 100 phần trăm do cách thiết kế. Cổng 2 của
kế hoạch yêu cầu ít nhất một thước đo khác nhau giữa các mức quant. Thước đo này có khác nhau. Nó đã
khác nhau trong mọi campaign, ở mọi commit.

**Model nghiên cứu viết được rất ít code compile được.** DeepSeek Coder V2 Lite ở Q4_K_M đề xuất
khoảng 25 operation mỗi lần chạy. Gần như operation nào cũng lùi về stub sau hai vòng sửa. Q8_0 làm
tốt hơn, nhưng vẫn phải dùng stub cho phần lớn những gì nó viết. Model coder của production đề xuất
ít operation hơn nhiều mỗi lần chạy, và khoảng một nửa trong số đó được giữ lại. Các dòng không cùng
cơ sở so sánh: một dòng dựa trên khoảng 25 operation, dòng kia dựa trên 3. Cột `ops_total` có mặt để
người đọc thấy điều đó trước khi so sánh stub rate.

**Vòng sửa ở cấp task có chạy, nhưng hiếm.** Trong phần lớn các lần chạy, `heal_attempts` là 0 và
`go_test_pass` là 5 trên 5. Cả hai đều do cách thiết kế: stub compile được và qua test. Trong một lần
chạy Q8_0, backend sinh ra build được, test của chính nó fail, và vòng sửa cấp task chạy chín lần.
Phải qua bốn campaign mới thấy cột đó dịch chuyển hai lần. Nó được báo cáo để không ai đọc số 0 như
một kết quả.

**Tốc độ và chất lượng đi theo hai hướng ngược nhau.** Q4_K_M nhanh hơn Q8_0 khoảng ba lần tính theo
tokens per second và dùng ít hơn khoảng 4 GB VRAM. Nó cũng gần như không tạo ra được gì compile được.
Với pipeline này, trên card này, mức quant nhanh hơn không phải là mức rẻ hơn.

**Chiến lược B từng không đo được gì, và giờ harness bắt được lỗi đó.** Trong campaign đầu tiên,
driver đặt `OLLAMA_KEEP_ALIVE=-1`. Lớp gửi request gửi giá trị đó dưới dạng chuỗi "-1". Ollama từ
chối mọi request, và schema dự phòng offline vẫn build xanh. Lần tổng hợp đầu tiên cho thấy B có stub
rate 0 phần trăm, dòng tốt nhất trong bảng. Sau đó có ba bản sửa. Lớp gửi request gửi một số nguyên
trần dưới dạng số. Pipeline đánh dấu một ý tưởng không có request model nào hoàn tất là chưa được
đo. Bộ tổng hợp loại bỏ những lần chạy đó và đếm chúng trong `runs_not_measured`. Cột đó bằng 0 ở
mọi dòng phía trên.

**Ba chiến lược là cùng một chiến lược trên card này.** Chi phí nạp lại và tokens per second giống
hệt nhau giữa A, B và C. Bản ghi `ollama ps` ở cuối lần chạy B cho thấy một model nằm trong bộ nhớ,
không phải hai. Planner nặng 9.3 GB trên đĩa và coder nặng 9.0 GB. Mỗi model cần KV cache và runtime
đi kèm, nên cặp này không vừa cùng lúc trong 16 GB. "Cả hai cùng nằm trong bộ nhớ" suy biến thành
đúng những gì A làm. Việc cả hai có vừa hay không tự nó là một kết quả, và câu trả lời là không.

**Sampling đã ghim cho ra hai đầu ra, không phải một.** Temperature 0, seed 42 và top_p 1 được đặt
trên mọi request. Với cặp model production, mọi lần chạy của mọi campaign đều rơi vào đúng một trong
hai đầu ra. Một đầu ra có hai trong ba operation bị thay bằng stub, đầu ra kia không có operation
nào bị thay. Trong một campaign, chiến lược A nhận đầu ra thứ nhất cả ba lần và B nhận đầu ra thứ
hai. Ở campaign kế tiếp, phân bổ đảo ngược: A nhận đầu ra thứ hai cả ba lần và B nhận đầu ra thứ
nhất. Một lần chạy rơi vào đầu ra nào phụ thuộc vào trạng thái server, không phụ thuộc vào chiến
lược. Với ba operation mỗi lần chạy, một lần đảo làm stub rate thay đổi một phần ba. Đó là lý do mọi
dòng đều ghi n và khoảng giá trị. Đó cũng là lý do không nên đọc cột stub rate trong bảng chiến lược
như tác động của chiến lược. Việc ghim determinism trên một server cục bộ là một ưu tiên mạnh, không
phải một phép chứng minh.

**Một thước đo thứ hai cũng là 100 phần trăm do cách thiết kế.** Trước campaign này, bước verify tính
một lời gọi là nội bộ khi có bất kỳ symbol nào mang tên trần của nó. Sau đó nó resolve lời gọi theo
chính tên trần đó. Vì vậy một repo Python luôn đạt 100 phần trăm resolve nội bộ. Giờ resolver đi
theo một lời gọi có tiền tố package qua các import của hàm gọi. Một lời gọi mà nó không định vị được
thì vẫn là chưa resolve. Trên cùng các repo SWE-bench, tỷ lệ resolve nội bộ giờ là 92.6 phần trăm
cho astropy và 96.1 phần trăm cho django. Số cạnh nội bộ trên các repo Go giảm tới một phần bảy. Các
lời gọi vào package mà index không chứa giờ được tính là bên ngoài, thay vì bị bắt nhầm. Đó là những
con số thật thay cho một mệnh đề luôn đúng. Cùng thay đổi đó giảm verify findings trên các backend
sinh ra từ vài trăm mỗi lần chạy, gần như toàn là lời gọi thư viện chuẩn, xuống còn 0.

**SWE-bench: đọc cột neighbourhood trước cột recall.** Bảng này là localization recall trên 60 task
đầu tiên của SWE-bench Verified theo thứ tự instance, gồm 22 task astropy và 38 task django. Nó không
phải solve rate. Hop 1 không thêm gì so với hop 0. Các định danh seed lấy từ nội dung issue hoặc đã
nằm sẵn trong các file gold, hoặc không. Hop 2 tăng recall trong khi neighbourhood trung vị phình tới
khoảng 420 file, tức hơn một nửa astropy và một phần sáu django. Một tấm lưới rộng như vậy bắt được
file gold nhờ độ rộng. Resolver chặt hơn đã thu nhỏ neighbourhood đó khoảng một phần mười mà recall
không đổi. Điều đó cho thấy độ rộng chưa bao giờ là thứ tạo ra kết quả. Quy tắc seed lấy tối đa 80
định danh từ nội dung issue theo đúng tên. Trong một repo 2,500 file, một cái tên như `Model` khớp ở
hàng trăm chỗ. Thước đo này trung thực về điều đó, vì kích thước neighbourhood được in ngay cạnh nó.
Một quy tắc seed chặt hơn là thứ tiếp theo cần xây. Con số sẽ giảm khi quy tắc đó được xây xong.

## 7. Hướng phát triển tiếp

Có hai hướng, chưa hướng nào được coi là đã xong.

Hướng thứ nhất là một kernel sinh token viết tay, đo bằng chính harness này. Kernel đó là phép nhân
ma trận với vector trên các trọng số đã quantize của model coder. Nó được profile bằng Nsight và so
với tokens per second mà Ollama đạt trong bảng quantization. Roofline cho việc đó là một phép chia:
băng thông bộ nhớ chia cho số byte trọng số phải đọc cho mỗi token. Dòng production ở trên đã đạt 96
phần trăm mức đó. Nhiệm vụ của kernel là tái hiện mức trần đó bằng code của chính tôi, và chỉ ra
khoảng cách còn lại nằm ở đâu.

Hướng thứ hai là đưa các graph luồng điều khiển đã render quay lại cho model làm ngữ cảnh sửa lỗi,
đặt sau một cờ, và đo nó đúng cách. Tôi dự đoán không có tác động với việc sửa code Go, vì compiler
đã báo cho model biết sai ở đâu. Tôi dự đoán có thể có tác động với COBOL và với việc làm giàu niềm
tin, nơi không có compiler để dựa vào. Kết quả sẽ được công bố dù thế nào, kể cả khi không có tác
động.

## 8. Ba thứ tôi tìm ra khi đọc lại code của chính mình

Runtime đến tay tôi ở trạng thái chưa tinh chỉnh, nên mỗi điều khiển thành một lượt quét có con số ở
cuối. Khi thước đo chất lượng chính hóa ra là 100 phần trăm do cách thiết kế, tôi ghi thẳng điều đó
vào bảng và xây một thước đo có thể dịch chuyển.

Thước đo hỏng không phải là thứ duy nhất lượt làm việc này lôi ra.

**Hai bug determinism, tìm ra khi đọc lại code của chính tôi.** Không bug nào đến từ một báo cáo lỗi.
Determinism là tuyên bố chịu lực của hệ thống này: temperature 0, seed cố định, đầu ra giống hệt
nhau. Bước resolve symbol đã phá vỡ nó. Nó lấy kết quả khớp đầu tiên khi duyệt một map trong Go, và
Go xáo ngẫu nhiên thứ tự đó. Hai symbol export có cùng tên ngắn có thể resolve khác nhau giữa các
lần chạy, và call graph lặng lẽ đổi hình dạng.

Tôi đã sửa nó, viết test, rồi chuyển sang việc khác. Sau đó hóa ra có một resolver thứ hai trên một
đường code khác, mang cùng lỗi đó, cộng thêm một lỗi tệ hơn. Nó hoàn toàn không ưu tiên theo tầng,
nên một symbol của thư viện chuẩn có thể chiếm lấy một lời gọi của dự án. Các test của tôi đã đi qua
đường code đã sửa và pass, trong khi bug nằm ngay bên cạnh. Bản sửa thứ hai xóa bản trùng lặp thay vì
sửa nó. Hai hàm trả lời cùng một câu hỏi theo hai cách khác nhau, và không có gì bắt chúng phải khớp.

**Sáu test đã fail vì sai lý do.** Bảy test đã fail một thời gian. Lần đọc đầu tiên, tôi cho rằng
chúng có vẻ do môi trường. Sáu test trong số đó không phải vậy. Ba test fail vì một hàm hỗ trợ test so khớp
node theo tên, trong khi node lời gọi lưu định danh ở một trường khác. Mọi lần tra cứu lặng lẽ không
tìm thấy gì, và một frontend đúng phải chịu lỗi. Hai test là do một lỗi định dạng khiến nhãn
flowchart hiển thị thành chữ vỡ. Một test khẳng định một quy tắc mà một phiên bản sau đã cố ý thay
thế. Chỉ test thứ bảy thực sự phụ thuộc nền tảng.

**Một resolver không thể trượt.** Bước verify đọc lại code sinh ra đã báo 100 phần trăm resolve nội
bộ trên mọi repo Python. Cùng lúc đó, nó báo hàng trăm lời gọi chưa resolve trên mọi backend sinh ra.
Cả hai con số đến từ cùng một lối tắt: một lời gọi được so khớp theo tên trần với mọi symbol mà index
chứa. Khi thay bằng cách đi theo lời gọi qua các import của hàm gọi, con số 100 thành 92.6 và 96.1
trên hai repo công khai, và hàng trăm findings thành 0. Mục 6 có cả hai con số.

Cả ba có chung một cơ chế bên dưới: một phép so sánh chỉ có thể trả về đúng một kết quả. Một thước
đo kẹt ở 100 phần trăm. Một bộ test xanh trên đúng đường code tôi tình cờ test. Sáu test đỏ mà tôi
đã sẵn sàng đổ cho nền tảng. Một resolver không thể trượt.

Chạy hệ thống rồi nhìn nó hoạt động thì không bắt được thứ nào trong đó. Tôi tìm ra cả ba khi đọc
lại code đã pass test, và hỏi mỗi con số sẽ trông thế nào nếu nó đang nói dối tôi.

*Mọi số đo thời gian là phép đo GPU cục bộ chạy native, lấy qua harness của chính dự án, trên cỗ máy
mô tả ở mục 0. Phương pháp nằm trong [benchmark tái lập được](03-reproducible-benchmarking.vi.md).
Tốc độ tuyệt đối phụ thuộc vào GPU. Hình dạng của mỗi đánh đổi thì vẫn đúng trên card khác.*
