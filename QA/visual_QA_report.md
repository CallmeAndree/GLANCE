# GLANCE Full S1–S5 x4 — Tổng hợp lỗi visual đã xác nhận

> Video: `GLANCE_full_S1-S5_x4_silent.mp4`  
> Phạm vi QA: rà frame-level, contact sheet 9 frame/sheet.  
> Chỉ giữ **lỗi thật đã xác nhận**; đã loại animation hợp lệ, transition có chủ ý và các mục không đủ bằng chứng.

---

## 00:03.00–00:03.33 — Ghost graph từ scene trước

**Lỗi:** Graph `User A–E` của scene trước vẫn còn hiện phía sau scene `TEXT CONTENT / GRAPH STRUCTURE`.

**Vấn đề:** Hai composition chồng nhau trong transition, background cũ vẫn đủ rõ để gây nhiễu.

**Sửa:** Fade/remove graph cũ hoàn toàn trước khi scene mới đạt trạng thái chính; tránh crossfade hai layout phức tạp cùng lúc.

---

## 00:06.80–00:07.20 — Ghost User cards/graph phía sau GLANCE

**Lỗi:** Các User card/graph cũ vẫn nhìn thấy phía sau `GLANCE for Context` và poster.

**Vấn đề:** Transition không opaque hoàn toàn.

**Sửa:** Fade out scene cũ về opacity 0 trước khi foreground mới xuất hiện rõ.

---

## 00:14.53–00:14.87 — Graph cũ còn phía sau CONTENT → A → STRUCTURE

**Lỗi:** Graph lớn từ scene trước vẫn hiện mờ phía sau pipeline mới.

**Vấn đề:** Vì graph chiếm diện tích lớn nên dù opacity thấp vẫn gây cảm giác scene bẩn.

**Sửa:** Xóa/fade graph cũ sớm hơn; nếu dùng overlay transition thì thêm background opaque thực sự.

---

## 00:16.87–00:17.40 — Ghost graph phía sau title TAG

**Lỗi:** Graph cũ vẫn còn hiện phía sau `TAG = Textual Content + Graph Structure`.

**Vấn đề:** Làm yếu title hierarchy và khiến visual center bị rối.

**Sửa:** Scene cũ phải biến mất hoàn toàn trước khi title/pipeline mới settle.

---

## 00:18.47–00:18.87 — Background graph còn tồn tại khi pipeline mới đã lên

**Lỗi:** Graph cũ vẫn còn phía sau foreground pipeline/prediction.

**Vấn đề:** Hai scene phức tạp cùng tồn tại trong frame giữa.

**Sửa:** Tách transition thành `fade old → clean dark frame → reveal new`, hoặc đảm bảo background mới che hoàn toàn scene cũ.

---

## 02:09.xx — Edge xuyên vào node trong graph Heuristic 1

**Lỗi:** Nhiều cạnh đi thẳng vào phần bên trong circle node thay vì dừng ở perimeter.

**Vấn đề:** Đây là lỗi geometry tồn tại ở trạng thái ổn định, không phải animation.

**Sửa:** Tính endpoint theo bán kính node hoặc mask edge dưới node.

---


## 02:29.7–02:30.0 — Hai trạng thái equation chồng glyph

**Lỗi:** Equation `d_i = ...` cũ và `CDensity(v_i) = ...` mới cùng tồn tại trong cùng vùng, glyph nhập vào nhau.

**Vấn đề:** Morph không giữ readability ở frame trung gian.

**Sửa:** Fade/transform theo từng nhóm glyph có correspondence, hoặc fade out equation cũ trước khi write equation mới.

---

## 05:21.67–05:21.93 — Edge highlight đỏ xuyên Node A

**Lỗi:** Stroke đỏ chạy vào bên trong Node A, tạo X/star trong tâm node.

**Vấn đề:** Z-order/highlight mask sai.

**Sửa:** Đặt highlight edge dưới node hoặc clip edge tại node boundary.

---

## 07:44.33–07:44.47 — Equation morph bị chồng số/bracket

**Lỗi:** Phép tính cũ `[1.10, 1.92, 0.98] / 4` và vector mới `[0.275, 0.480, 0.245]` chồng trực tiếp lên nhau.

**Vấn đề:** Số, bracket và fraction cùng chiếm một vùng trong frame giữa.

**Sửa:** Tách morph thành hai phase hoặc dùng `ReplacementTransform` theo nhóm tương ứng thay vì transform toàn expression cùng lúc.

---

## 08:03.00 — `RAW TEXT t_A` bị double/ghost text

**Lỗi:** Nội dung `"Improving Graph Neural Networks..."` xuất hiện chồng hai bản trong lúc `encode text` xuất hiện.

**Vấn đề:** Text morph tạo double glyph rõ trong một frame.

**Sửa:** Không để source text và target text cùng opacity cao; fade source trước hoặc transform từng line.

---

## 08:04.80 — Card `x_A` flash thành box xanh trống

**Lỗi:** `x_A` biến thành rounded rectangle lime đặc và toàn bộ text biến mất đúng một frame, sau đó text quay lại.

**Vấn đề:** Artifact 1-frame do fill/text layer không đồng bộ.

**Sửa:** Animate fill/background ở layer riêng phía dưới; giữ text layer tồn tại xuyên suốt.

---

## 08:42.20–08:42.74 — Card `GLANCE` chạy xuyên graph

**Lỗi:** Trong lúc re-layout/thu nhỏ, card `GLANCE` di chuyển ngang trực tiếp qua node và edge.

**Vấn đề:** Path animation và z-order làm hai semantic component va vào nhau nhiều frame.

**Sửa:** Cho card đi theo path tránh graph, hoặc fade/move graph trước rồi mới move card.

---

## 08:59.20–08:59.27 — Stray glyph còn sót trong transition

**Lỗi:** Một mảnh ký tự/glyph đơn lẻ còn lại ở giữa-trái frame khi architecture đã biến mất và `f_A` bắt đầu xuất hiện.

**Vấn đề:** Debris 1-frame.

**Sửa:** Đảm bảo toàn bộ submobject của expression cũ được remove/fade cùng group.

---

## 09:04.xx — Sai semantic label `a_E`

**Lỗi:** Scene đang theo node A (`f_A → router → a_A`, equation `a_A = π(f_A)`), nhưng bên dưới lại xuất hiện `a_E = 0.81`, sau đó mới đổi thành `a_A = 0.86`.

**Vấn đề:** Lỗi nội dung/semantic identity, không chỉ visual.

**Sửa:** Dùng thống nhất node A xuyên suốt scene; sửa label thành `a_A` ngay từ lần xuất hiện đầu.

---

## 11:17.xx–11:22.xx — Arrow xanh đè lên `SAME TRUE LABEL y_A`

**Lỗi:** Đường/đầu arrow xanh cắt trực tiếp vùng cuối của label `SAME TRUE LABEL y_A`.

**Vấn đề:** Overlap tồn tại nhiều frame.

**Sửa:** Dời label hoặc điều chỉnh source/target của arrow để có khoảng clearance rõ quanh text.

---

## 11:22.10–11:22.40 — Footnote quá nhỏ và tồn tại quá ngắn

**Lỗi:** Footnote dài về `ℓ_v^LLM ... full GNN + LLM + refiner C branch...` chỉ xuất hiện khoảng 0.3 giây ở bản x4 và nằm rất nhỏ sát đáy.

**Vấn đề:** Không thể đọc thực tế; hierarchy và timing không hợp lý.

**Sửa:** Rút gọn nội dung, tăng font size, đặt cao hơn và giữ đủ lâu; nếu thông tin phụ thì chia sang scene riêng.

---

## 11:25.40 — `gain 2.00` bị duplicate

**Lỗi:** Hai copy `gain 2.00` gần như cùng vị trí, tạo double-outline/double-text.

**Vấn đề:** Duplicate object trong frame trung gian.

**Sửa:** Remove/fade object cũ trước khi tạo target hoặc dùng một object duy nhất để transform.

---

## 11:25.46 — `gain 2.00` xuyên qua box `ℓ_v^LLM = 0.30`

**Lỗi:** Card `gain 2.00` đang move xuyên trực tiếp qua box loss.

**Vấn đề:** Hai card semantic độc lập overlap trong transition.

**Sửa:** Đổi movement path hoặc sequencing: move/fade box thứ nhất trước, rồi mới đưa card thứ hai vào vị trí.

---

## 12:57–13:04 — Result cluster quá nhỏ so với canvas

**Lỗi:** Toàn bộ large-scale result chỉ chiếm vùng nhỏ ở phía trên/giữa, trong khi phía dưới bỏ trống rất nhiều.

**Chi tiết:** Các thông tin như `2.45M NODES · ~62M EDGES`, `K~1, batch 64`, `GCNII: 81.8` quá nhỏ và mờ ở bản x4.

**Sửa:** Scale toàn result block lớn hơn, tận dụng chiều cao frame và tăng size cho số liệu chính.

---

## 13:09–13:17 — Five takeaways quá nhỏ, quá nhạt

**Lỗi:** 5 takeaway dài nhưng font nhỏ, contrast thấp và để nhiều empty space không cần thiết.

**Vấn đề:** Đây là phần kết luận quan trọng nhưng gần như không đọc kịp ở tốc độ x4.

**Sửa:** Tăng font/contrast, rút gọn câu, giảm số dòng trên một screen hoặc chia thành 2 scene.

---

# Tổng quan lỗi cần ưu tiên

### Priority 1 — Lỗi render/transition rõ
- Ghost scene cũ: `00:03`, `00:06.8`, `00:14.5`, `00:16.9`, `00:18.5`
- Equation/text chồng glyph: `02:29.7`, `07:44.3`, `08:03`
- Flash/missing content: `08:04.80`
- Stray glyph: `08:59.20`
- Duplicate object: `11:25.40`

### Priority 2 — Overlap / geometry / z-order
- Edge xuyên node: `02:09`, `02:20`, `05:21`
- Annotation đè graph: `02:10`, `02:14`
- Label đè edge: `02:20`
- Card chạy xuyên graph/card khác: `08:42`, `11:25`
- Arrow đè text: `11:17–11:22`

### Priority 3 — Semantic / readability / composition
- Sai `a_E` thay vì `a_A`: `09:04`
- Footnote không đọc được: `11:22`
- Result block quá nhỏ: `12:57–13:04`
- Takeaways quá nhỏ/nhạt: `13:09–13:17`

---

## Các mục đã loại sau khi double-check

Không tính là lỗi:
- Paper → node morph khoảng `00:10`
- Router chạy ra mép khoảng `09:24`
- Các trạng thái `Write()`/typewriter bình thường
- Các fade/morph hợp lệ không gây overlap hoặc artifact thực tế
