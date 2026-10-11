[English](03-reproducible-benchmarking.md) · **Tiếng Việt**

# Benchmark tái lập được và regression gate

### Baseline đóng băng, gate, tính tất định, và hai thước đo không đo được gì

> **Bối cảnh:** tôi tinh chỉnh cả hai dự án ở đây dựa trên các phép đo cố định, lặp lại được.
> Dự án thứ nhất là gen-system, có harness và kết quả nằm trong [repository của nó](https://github.com/hpdkhoa/gen-system).
> Dự án thứ hai là HieuLuat, đã ngừng phát triển sau khi công ty được mua lại. Harness của nó vẫn
> không công khai, nhưng các dòng số liệu tuân theo cùng quy tắc. **Nội dung bài:** ba quy tắc; thế
> nào là một baseline đóng băng và một gate; cách tôi làm cho các lần chạy lặp lại được và những chỗ
> chúng không lặp lại được; và hai lần một thước đo chất lượng hóa ra không đo được gì. Mỗi bài học
> trong hai bài học đó đã lấy của tôi trọn một campaign.

---

## 1. Ba nguyên tắc

Tôi đã phá cả ba ít nhất một lần.

1. Đo trước và sau, lần nào cũng vậy. Tôi báo mọi thay đổi so với một baseline đã ghi lại. Không có
   baseline thì tôi không đưa ra nhận định.
2. Làm cho các lần chạy lặp lại được khi công việc cho phép. Nếu không, chạy lại là con số đổi, và
   bạn không tách được thay đổi của mình khỏi nhiễu.
3. Gắn chất lượng với một thứ khách quan. Tốc độ đổi bằng việc âm thầm mất chất lượng không phải là
   thắng lợi. Vì vậy tôi đo chất lượng song song với hiệu năng, và không bao giờ mặc định là nó giữ
   nguyên.

## 2. Baseline đóng băng

Baseline là một phép đo đã ghi lại của hệ thống trước một thay đổi. Nó gắn với một phiên bản, và tôi
đo nó trong điều kiện cố định. Nó nằm trong một file.

Trong cả hai dự án, tôi báo mọi tối ưu hóa so với một baseline như vậy. Nhờ đó người khác kiểm tra
được một câu như "thay đổi này cải thiện throughput".

## 3. Regression gate

Đo sau khi thay đổi chỉ có ích nếu có người xem kết quả. Gate thì khiến sự suy giảm làm build thất
bại.

Trong gen-system, harness có thể diff một lần chạy benchmark với một baseline đã commit. Nếu độ lệch
vượt quá ngưỡng dung sai, lệnh thoát với mã khác 0. Baseline COBOL đóng băng hoạt động theo cách
này. Đó là một repository COBOL của bên thứ ba ở một commit cố định, kèm recall phân giải đã ghi
lại. Gate chặn một thay đổi parser làm giảm recall đó, thay vì để ai đó phát hiện ra vài tuần sau.

Cùng ý tưởng đó đã áp dụng cho các eval set đã gán nhãn của HieuLuat. Tôi chỉ chấp nhận một thay đổi
trên luồng retrieval nếu chất lượng đã đo giữ nguyên hoặc tốt hơn trên các trường hợp cố định đó.
Tôi loại một index nhanh hơn nhưng âm thầm làm giảm recall, thay vì đưa nó vào sản phẩm.

## 4. Tính khả tái lập

Khi công việc cho phép, tôi làm cho các lần chạy deterministic. gen-system sinh output ở temperature
0 với seed cố định. Một bộ kiểm thử xác nhận rằng cùng một prompt cho ra đúng một output duy nhất qua
các lần chạy lặp lại.

Khi đó khác biệt giữa hai lần chạy phản ánh thay đổi bạn đã làm, không phải biến động ngẫu nhiên.
Khi một thành phần mang tính ngẫu nhiên, tôi chạy lặp lại nhiều lần và báo cáo một khoảng giá trị
thay vì một con số duy nhất.

Việc cố định này khiến các lần chạy nhiều khả năng lặp lại. Nó không chứng minh được điều đó. Bộ kiểm
thử determinism đạt trên một prompt đơn lẻ. Toàn bộ pipeline sinh vẫn rơi vào một trong hai output
khác nhau qua các lần chạy lặp lại, trên cùng model với cùng seed. Rơi vào output nào phụ thuộc vào
trạng thái của server local, không phụ thuộc vào bất cứ thứ gì trong lần chạy. Đó là lý do mọi bảng
gen-system trong repository này đều ghi `n` và một khoảng giá trị. Tôi không báo cáo một khác biệt
chỉ xuất hiện ở một trong ba lần chạy như một phát hiện.

## 5. Chọn thước đo chất lượng có thể thay đổi

Cả hai dự án đều đo chất lượng trực tiếp thay vì qua một thước đo gián tiếp. gen-system đã chọn sai
thước đo ở lần đầu.

Kế hoạch ban đầu là báo tỷ lệ compile thành công. Code sinh ra có build được không? Con số trả về là
100 phần trăm ở mọi lần chạy. Công cụ thay một thao tác bị lỗi bằng một stub compile được. Thước đo
này không thể giảm, nên nó không đo được gì.

Thước đo thay thế đếm những gì thay đổi. Nó đếm lượng logic sinh ra vượt qua gate compile thay vì
quay về stub, và số vòng sửa lỗi cần để đạt được điều đó. Chi tiết nằm ở
[mục 4 của writeup về inference](02-gen-system-inference-optimization.vi.md).

Điều này quan trọng nhất với công việc quantization, nơi toàn bộ rủi ro là mất chất lượng một cách
âm thầm. Phần lớn các writeup về inference chỉ có thể đưa ra một đường cong perplexity và hy vọng nó
phản ánh đúng mức hữu ích. Một thước đo khách quan nhưng bị kẹt còn tệ hơn một thước đo gián tiếp,
vì nó trông giống bằng chứng. Vì vậy tôi kiểm tra xem thước đo đó có thay đổi được hay không.

Chuyện này xảy ra lần thứ hai, theo chiều ngược lại. Bước verify đọc lại code đã sinh và chấm tỷ lệ
phân giải nội bộ đạt 100 phần trăm trên mọi repository Python mà nó gặp. Nó tính một lời gọi là nội
bộ khi có bất kỳ symbol nào mang tên trần của lời gọi đó. Sau đó nó phân giải lời gọi theo chính tên
trần đó, nên nó không thể trượt. Khi tôi sửa resolver để nó lần theo lời gọi qua các import của nơi
gọi, con số 100 đó trở thành 92.6 và 96.1 trên hai repository công khai. Một con số giảm xuống khi
công cụ trở nên chặt chẽ hơn là một con số đo được điều gì đó. Bài kiểm thử cố định cho lỗi này nạp
cùng một repository khi có và khi không gắn thư viện chuẩn, và yêu cầu recall nội bộ phải bằng nhau.

HieuLuat gặp cùng dạng vấn đề từ phía bên kia: một giá trị recall đứng yên ở 0.75 với mọi index và
mọi thiết lập reranker. Mục 6 của [writeup về tìm kiếm pháp luật](01-hieuluat-retrieval-optimization.vi.md)
đọc con số đứng yên đó là giới hạn trần của embedding model, chứ không phải một kết quả về index.
Mục đó cũng chỉ ra một phép đo có thể phân định vấn đề: recall tại 50.

## 6. Phạm vi áp dụng

- [Writeup về luồng tìm kiếm pháp luật](01-hieuluat-retrieval-optimization.vi.md): recall và latency
  đo trên các eval set cố định theo phương pháp này. Mục 6 trong đó là một ví dụ cụ thể về cách đọc
  đúng một con số đứng yên.
- [Writeup về inference](02-gen-system-inference-optimization.vi.md): tốc độ, VRAM, tỷ lệ stub và số
  vòng sửa lỗi đều chạy qua harness benchmark so với các baseline đóng băng.
- [Thư mục benchmarks](../benchmarks/README.vi.md): chính các bảng kết quả đo, và môi trường tôi
  dùng để đo chúng.

## 7. Giá trị chứng minh của thứ tự commit

Tôi commit bộ tác vụ trước lần chạy đầu tiên, để tôi không thể nắn nó theo kết quả.

Lịch sử công khai của gen-system bắt đầu từ ngày tôi chuẩn bị repository để phát hành, nên người đọc
không thấy những tuần trước đó. Điều người đọc có thể kiểm tra là thứ tự bên trong lịch sử đó. Commit
thêm bộ tác vụ đứng trước commit thêm thư mục kết quả. File tác vụ cũng ghi ngày đóng băng. Mỗi
campaign còn giữ các file thô kèm danh sách hash, nên người đọc dựng lại được mọi bảng. Bench của
HieuLuat là riêng tư, nên các dòng của nó không có dấu vết như vậy.

Mục 5 là phần mất nhiều thời gian nhất. Tôi giữ một thước đo suốt mấy tháng mới nhận ra nó chỉ trả
về đúng một giá trị.

*Các con số nằm trong hai writeup dự án, và chúng phụ thuộc vào card trong
[ENVIRONMENT.vi.md](../benchmarks/ENVIRONMENT.vi.md). Các quy tắc ở đây thì không.*
