# Labs: máy nhìn vật lý qua con số

Các MCP server giúp mô hình dựng và chấm việc 3D bằng số đo: bộ phận, cơ thể, điểm chạm, lực.
[English](README.md)

![Trước 7 lab và 152 công cụ; sau 5 lab và 28 công cụ](labs-map.svg)

## Mục tiêu, theo lời chủ dự án

| # | Lời |
|---|---|
| G1 | "in real life that will not happen" (không xuyên mesh, không ngón xoắn: tường cứng) |
| G2 | "a virtual world like matrix idea where every thing every poly control by numbers, start from the hand and the gun" |
| G3 | "numbers that have meaning to really appreciate physics in digital world so after the physics and object interact is correct I can start the creation automatically" |

## Các lab

Ngày 2026-11-01, 152 công cụ trong 7 lab gộp thành 28 công cụ trong 5 lab. Mỗi công cụ nhận một action và tham số
của nó, rồi gọi đúng hàm cũ của lab, không đổi. Test kiểm mỗi công cụ cũ trong 152 là đúng một action.

| Lab | Công cụ | Trước | Làm gì | Bước |
|---|---|---|---|---|
| [objectlab-mcp](https://github.com/hpdkhoa/objectlab-mcp) | 7 | 57 | Đặt tên mọi bộ phận của vật, đo từ nguồn, dựng, phủ bề mặt | 1 |
| [holdlab-mcp](https://github.com/hpdkhoa/holdlab-mcp) | 8 | 40 | Đo tay và cánh tay, giữ giới hạn khớp làm tường, đặt tay cầm theo luật | 2, 3, 4 |
| [gatelab-mcp](https://github.com/hpdkhoa/gatelab-mcp) | 6 | 26 | Chấm mọi kết quả theo tường và đánh giá của chủ dự án | 5, 7 |
| [createlab-mcp](https://github.com/hpdkhoa/createlab-mcp) | 4 | 21 | Dựng rig, tư thế cầm và clip cho vật mới | 6 |
| [ocrlab-mcp](https://github.com/hpdkhoa/ocrlab-mcp) | 3 | 8 | Đọc chữ, đường nét và đường viền từ trang và ảnh | nguồn |

Các lab bên dưới vẫn là package riêng: poselab-mcp, weaponlab-mcp, modellab-mcp, coatinglab-mcp, feellab-mcp,
fakepose-mcp. Kiểm lực (công cụ thứ 29) đến ở bước 4.

## Bằng chứng, từ lần chạy mới nhất

Từ video tiến hóa của các lab (2026-10-27, 191 giây).

| | |
|---|---|
| ![Tiến hóa: tám lab trong hai mươi ngày](media/evolution-timeline.jpg) | ![Lab nào chuyển gì cho lab sau](media/collaboration.jpg) |
| Tám lab trong hai mươi ngày, từ git log | Lab nào chuyển gì cho lab sau |

Trước và sau trên cùng một màn hình, cùng clip chạy song song: thay đạn M16A2 và kiểm buồng đạn AR-15.

![Trước và sau, cùng clip chạy song song](media/before-after.gif)

| | |
|---|---|
| ![Cổng kiểm tay: FAIL thành PASS](media/hand-gate-fail-to-pass.jpg) | ![M1911A1: bản vẽ so với mô hình](media/m1911a1-blueprint-vs-model.jpg) |
| Cổng kiểm tay ở báng AR-15: FAIL (ngón cái lún 0,89 cm) thành PASS | M1911A1: khung dài 21,827 cm so với 21,826 in trên bản vẽ |

![Bằng số](media/in-numbers.jpg)

## Các bước

| Bước | Dựng |
|---|---|
| 1 | Nghĩa trên vật: mọi poly thuộc một bộ phận có tên |
| 2 | Nghĩa trên cơ thể: da đo được, giới hạn khớp có nguồn |
| 3 | Luật chạm: bộ phận nào chạm bộ phận nào, loại chạm và hướng nắm |
| 4 | Kiểm lực: tay giữ vững trước trọng lượng và giật |
| 5 | Giải và chấm: tường cứng, mọi số báo kèm nghĩa của nó |
| 6 | Tạo tự động, sau khi bước 1 đến 5 đạt trên một khẩu súng đã duyệt |
| 7 | Đánh giá của chủ dự án thành phép kiểm; số lần chấm đạt sai về 0 |

Kế hoạch đầy đủ: [MEANING_PLAN.md](https://github.com/hpdkhoa/poselab-mcp/blob/main/docs/MEANING_PLAN.md).
