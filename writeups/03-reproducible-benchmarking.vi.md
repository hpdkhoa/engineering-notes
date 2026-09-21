[English](03-reproducible-benchmarking.md) · **Tiếng Việt**

# Benchmark tái lập được và regression gate

### Phương pháp khiến mọi con số khác trong repository này đáng để đọc

> **Bối cảnh:** cả hai dự án ở đây đều được tinh chỉnh dựa trên các phép đo cố định, lặp lại được.
> Dự án thứ nhất là gen-system, có harness và kết quả nằm trong [repository của nó](../projects/gen-system/README.vi.md).
> Dự án thứ hai là HieuLuat, có harness không công khai nhưng các dòng số liệu tuân theo cùng quy
> tắc. **Nội dung bài:** ba quy tắc; thế nào là một baseline đóng băng và một gate; cách làm cho các
> lần chạy lặp lại được và những chỗ chúng không lặp lại được; và hai lần một thước đo chất lượng
> hóa ra không đo được gì. > Mỗi bài học trong hai bài học đó đã lấy của tôi trọn một campaign.

---

## 1. Ba quy tắc

Ba quy tắc, và tôi đã phá cả ba ít nhất một lần.

1. **Đo trước và sau, lần nào cũng vậy.** Mọi thay đổi đều được báo cáo so với một baseline đã ghi
   lại. Không có baseline thì không có nhận định.
2. **Làm cho các lần chạy lặp lại được khi công việc cho phép.** Nếu không, chạy lại là con số đổi, và bạn không tách được thay đổi của mình khỏi nhiễu.
3. **Gắn chất lượng với một thứ khách quan.** Tốc độ đổi bằng việc âm thầm mất chất lượng không
   phải là thắng lợi. Vì vậy chất lượng được đo song song với hiệu năng, không bao giờ được mặc định
   là giữ nguyên.

## 2. Baseline đóng băng

Baseline là một phép đo đã ghi lại của hệ thống trước một thay đổi. Nó gắn với một phiên bản và được
thực hiện trong điều kiện cố định. Nó nằm trong một file, không nằm trong đầu tôi.

Mọi tối ưu hóa trong cả hai dự án đều được báo cáo so với một baseline như vậy. Nhờ đó một câu như
"thay đổi này cải thiện throughput" kiểm tra được, thay vì là điều người đọc phải tin suông.

## 3. Regression gate

Phiên bản mạnh hơn của "đo sau" là làm cho mọi sự suy giảm tự động khiến build thất bại.

Trong gen-system, một lần chạy benchmark có thể được diff với một baseline đã commit. Nếu độ lệch
vượt quá ngưỡng dung sai, lệnh thoát với mã khác 0. Baseline COBOL đóng băng hoạt động theo cách
này: một repository COBOL của bên thứ ba ở một commit cố định, với recall phân giải đã được ghi lại.
Một thay đổi parser làm giảm recall đó sẽ bị gate chặn lại, không phải vài tuần sau mới phát hiện.

Cùng ý tưởng đó áp dụng cho các eval set đã gán nhãn của HieuLuat. Một thay đổi trên luồng retrieval
chỉ được chấp nhận nếu chất lượng đã đo giữ nguyên hoặc tốt hơn trên các trường hợp cố định đó. Một
index nhanh hơn nhưng âm thầm làm giảm recall sẽ bị loại, không được đưa vào sản phẩm.

## 4. Khả năng lặp lại

Khi công việc cho phép, các lần chạy được làm cho deterministic. gen-system sinh output ở temperature
0 với seed cố định. Một bộ kiểm thử xác nhận rằng cùng một prompt cho ra đúng một output duy nhất qua
các lần chạy lặp lại.

Lợi ích là khác biệt giữa hai lần chạy phản ánh thay đổi bạn đã làm, không phải biến động ngẫu
nhiên. Khi một thành phần thực sự mang tính ngẫu nhiên, câu trả lời trung thực là chạy lặp lại nhiều
lần và báo cáo một khoảng giá trị, không phải một con số duy nhất.

Việc cố định này tạo ra một thiên hướng mạnh, không phải một sự chứng minh. Bộ kiểm thử determinism
đạt trên một prompt đơn lẻ. Toàn bộ pipeline sinh vẫn rơi vào một trong hai output khác nhau qua các
lần chạy lặp lại, trên cùng model với cùng seed. Rơi vào output nào phụ thuộc vào trạng thái của
server local, không phụ thuộc vào bất cứ thứ gì trong lần chạy. Đó là lý do mọi bảng gen-system trong
repository này đều ghi `n` và một khoảng giá trị. Một khác biệt chỉ xuất hiện ở một trong ba lần chạy
không được báo cáo như một phát hiện.

## 5. Chọn một thước đo chất lượng thực sự có thể thay đổi

Cả hai dự án đều đo chất lượng trực tiếp thay vì qua một thước đo gián tiếp. Đó là phần có ích.
Nhưng chọn thước đo khó hơn vẻ ngoài của nó, và gen-system đã chọn sai ở lần đầu.

Kế hoạch ban đầu là báo cáo tỷ lệ compile thành công. Code được sinh ra có build được không? Con số
trả về là 100 phần trăm ở mọi lần chạy. Không phải vì model hoàn hảo, mà vì công cụ thay một thao tác
bị lỗi bằng một stub compile được. Thước đo này không thể giảm, nên nó không đo được gì.

Thước đo thay thế đếm những gì thực sự thay đổi. Đó là lượng logic được sinh ra vượt qua gate compile
thay vì quay về stub, và số vòng sửa lỗi cần để đạt được điều đó. Chi tiết nằm ở
[mục 4 của writeup về inference](02-gen-system-inference-optimization.vi.md).

Điều này quan trọng nhất với công việc quantization, nơi toàn bộ rủi ro là mất chất lượng một cách
âm thầm. Phần lớn các writeup về inference chỉ có thể đưa ra một đường cong perplexity và hy vọng nó
phản ánh đúng mức hữu ích. Một thước đo khách quan nhưng bị kẹt còn tệ hơn một thước đo gián tiếp,
vì nó trông giống bằng chứng. Vì vậy bài học không chỉ là chọn một thước đo khách quan. Bài học là
kiểm tra xem thước đo đó có thực sự thay đổi được hay không.

Chuyện này xảy ra lần thứ hai, theo chiều ngược lại. Bước verify đọc lại code đã sinh và chấm tỷ lệ
phân giải nội bộ đạt 100 phần trăm trên mọi repository Python mà nó gặp. Nó tính một lời gọi là nội
bộ khi có bất kỳ symbol nào mang tên trần của lời gọi đó. Sau đó nó phân giải lời gọi theo chính tên
trần đó, nên nó không thể trượt. Khi resolver được sửa để lần theo lời gọi qua các import của nơi
gọi, con số 100 đó trở thành 92.6 và 96.1 trên hai repository công khai. Một con số giảm xuống khi
công cụ trở nên chặt chẽ hơn là một con số đo được điều gì đó. Bài kiểm thử cố định cho lỗi này nạp
cùng một repository khi có và khi không gắn thư viện chuẩn, và yêu cầu recall nội bộ phải bằng nhau.

HieuLuat gặp cùng dạng vấn đề từ phía bên kia: một giá trị recall đứng yên ở 0.75 với mọi index và
mọi thiết lập reranker. Mục 6 của [writeup về tìm kiếm pháp luật](01-hieuluat-retrieval-optimization.vi.md)
đọc con số đứng yên đó là giới hạn trần của embedding model, chứ không phải một kết quả về index.
Mục đó cũng chỉ ra một phép đo có thể phân định vấn đề: recall tại 50.

## 6. Phương pháp này xuất hiện ở đâu

- [Writeup về luồng tìm kiếm pháp luật](01-hieuluat-retrieval-optimization.vi.md): recall và latency
  được đo trên các eval set cố định theo phương pháp này. Mục 6 trong đó là một ví dụ cụ thể về cách
  đọc đúng một con số đứng yên.
- [Writeup về inference](02-gen-system-inference-optimization.vi.md): tốc độ, VRAM, tỷ lệ stub và số
  vòng sửa lỗi đều chạy qua harness benchmark so với các baseline đóng băng. Nguồn gốc của mọi bảng
  được in ngay bên dưới bảng đó.
- [Thư mục benchmarks](../benchmarks/README.vi.md): chính các bảng kết quả đo, môi trường nơi chúng
  được đo, và nơi lưu manifest và attestation của campaign gen-system.

## 7. Thứ tự commit chứng minh được gì, và không chứng minh được gì

Baseline làm trước, và bộ tác vụ được commit trước lần chạy đầu tiên để không thể nắn nó theo kết
quả. Chất lượng nằm sau một gate, các lần chạy giữ cho lặp lại được ở những chỗ công việc cho phép.
Chỉ có vậy, và phần lớn là chuyện sổ sách.

Một lưu ý trung thực về chuyện đó. Lịch sử công khai của gen-system bắt đầu từ ngày
repository được chuẩn bị để phát hành, nên người đọc không thấy được những tuần trước đó. Điều người
đọc có thể kiểm tra là thứ tự bên trong lịch sử đó: commit thêm bộ tác vụ đứng trước commit thêm thư
mục kết quả. Ngày đóng băng cũng được ghi trong file tác vụ. Mỗi campaign kết thúc bằng một attestation và một manifest liệt kê mọi file dữ liệu thô kèm hash,
nên một con số trong writeup truy được về file chứ không truy về trí nhớ của tôi. Các dòng số liệu của HieuLuat không có
được dấu vết đó, vì harness không công khai. Các bảng nói điều đó thay vì ngầm ý ngược lại.

Mục 5 là phần mất nhiều thời gian nhất. Tôi giữ một thước đo suốt mấy tháng mới nhận ra nó chỉ trả
về đúng một giá trị.

*Các con số nằm trong hai writeup dự án, và chúng phụ thuộc vào card trong
[ENVIRONMENT.vi.md](../benchmarks/ENVIRONMENT.vi.md). Các quy tắc ở đây thì không.*
