[English](README.md) · **Tiếng Việt**

# Beastwarden: một game roguelite chiến thuật deterministic

> Một game chiến thuật theo lượt trên lưới, chạy trên trình duyệt, viết bằng TypeScript, dùng Vite
> và Pixi. Lõi mô phỏng là thuần, dùng seed và deterministic. Bộ test cưỡng chế thiết kế, thay vì
> chỉ mô tả nó.
>
> > Đây cũng là chỗ tôi điều hành việc phát triển có AI hỗ trợ, theo các quy tắc do máy kiểm tra.
> Hai dự án kia nói về chuyện đó. Dự án này phải sống với nó. Mã nguồn còn riêng tư trong lúc game
> đang làm dở. Trang này nói về kiến trúc và cách tôi làm việc trên nó.

---

## Thông tin nhanh

- **Nền tảng:** TypeScript, với client web dùng Vite và Pixi
- **Test:** 1,993 test đạt ở baseline đã xác minh gần nhất
- **Tính thuần của lõi:** không DOM, không `Date.now`, không `Math.random` trong lõi mô phỏng. Điều này
  được cưỡng chế bằng quy tắc lint và các guard tự viết, không dựa vào quy ước
- **Determinism:** cùng seed thì mọi thứ đều giống hệt. Forecast trận đánh phải đúng bằng kết quả xúc
  xắc thực tế
- **Quy trình:** một roadmap gồm các gói công việc có giới hạn, và một verify gate phải qua trước khi
  bất kỳ phiên nào kết thúc: typecheck, lint, guard tự viết, chạy toàn bộ test, và build

## Các quyết định thiết kế, và lý do

**Lõi deterministic thuần, được cưỡng chế bằng công cụ.** Phần mô phỏng trong `src/core` là một hàm
thuần của state và seed. Đó không phải chuyện gu. Một dự báo chỉ trung thực khi dự báo và trận đánh chạy cùng một đoạn code.

Giao diện có thể dự đoán kết quả trận đánh bằng cách chạy chính lõi mà trận đánh sẽ chạy. Sau đó một test khẳng định dự đoán và lần tung xúc xắc thật không bao giờ lệch nhau. Cũng là lý do
gen-system sinh code ở temperature 0. Một test bắn vào mục tiêu di động thì chứng minh được gì.

**Quy tắc là guard, không phải comment.** Hai guard tự viết chạy trong CI cạnh lint và typecheck.

Guard thứ nhất cấm hẳn pattern cờ "is dead". Chết nghĩa là bị xóa. Một entity không còn tồn tại thì
không thể nửa sống nửa chết ở một chỗ khác trong state.

Guard thứ hai đánh dấu mọi symbol được export mà không có gì ngoài test import. Nó siết dần từ một
allow list tường minh, nên phần public không dùng đến không thể âm thầm tích tụ.

Một quy tắc mà reviewer phải tự nhớ là một quy tắc nên để máy kiểm tra.

**Union đóng thay vì plugin mở.** Thêm nội dung mới, ví dụ một skill, chỉ là cấu hình. Thêm một loại
effect mới hoặc một luật xúc xắc mới là thay đổi code. Mọi handler switch trên kiểu đó đều phải xử
lý nó thì build mới qua.

Trình biên dịch liệt kê không gian thiết kế. Thêm một case mà không xử lý ở mọi nơi là lỗi kiểu,
không phải bất ngờ lúc chạy.

**AI hỗ trợ, con người điều hành, với kỷ luật được ghi thành văn bản.** Game được xây dựng theo các
gói công việc có giới hạn, qua các phiên có AI hỗ trợ, theo một thỏa thuận thường trực.

Các quy tắc ở trên không thể thương lượng. Mọi phiên đều kết thúc với toàn bộ verify gate xanh. Sổ
theo dõi tiến độ được cập nhật, để phiên sau bắt đầu từ sự thật đã xác minh thay vì từ trí nhớ lạc
quan.

gen-system đánh vào vấn đề đó từ phía công cụ. Còn ở đây tôi là người ra lệnh rồi sống với thứ nhận
về, và chuyện đó dạy cho những bài học khác.

## Vì sao nó nằm ở đây

Cùng một canh bạc với HieuLuat và gen-system, đánh lần thứ ba ở một ngôn ngữ khác và một lĩnh vực
khác: đưa tính đúng đắn vào từ thiết kế, rồi để máy cưỡng chế nó.

Đây cũng là thứ duy nhất trong ba thứ mà bạn chơi được. Rê chuột xem forecast sát thương, nhìn xúc
xắc rơi đúng con số đó, và tuyên bố về determinism thôi làm một gạch đầu dòng.

## Công nghệ sử dụng

TypeScript. Vite. Pixi cho WebGL 2D. Vitest. Guard lint tự viết. Bộ sinh số ngẫu nhiên có seed trong
lõi mô phỏng. DragonBones cho animation khung xương.

## Những gì không có ở đây, và lý do

Game đang được phát triển tích cực, nên mã nguồn, nội dung và tài liệu thiết kế tạm thời để private.
Các tuyên bố ở trên mô tả những gì công cụ cưỡng chế, và số lượng test lấy từ baseline đã xác minh
gần nhất.
