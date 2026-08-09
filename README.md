# GLANCE — Video giới thiệu paper

Video giải thích paper **"GLANCE for Context: Learning When to Leverage LLMs for
Node-Aware GNN–LLM Fusion"** (Loveland, Yang & Koutra, University of Michigan,
arXiv:2510.10849v1, 12 Oct 2025).

Video được dựng bằng **Manim Community Edition**. Mỗi thành viên sở hữu một
section riêng, render ra một file `.mp4` riêng, sau đó ghép lại bằng `ffmpeg`.

---

## Phân công

| Section | Nội dung | Thành viên | File |
|---|---|---|---|
| 0.1 | Related Work (Static / Adaptive GNN–LLM fusion, research gap) | **Hoàng Phan** | `sections/s0_background/s0a_related_work.py` |
| 0.2 | Preliminaries (TAG, node classification, message passing, LLM-as-Embedder/Predictor, $h_v$ & $\bar d_v$) | **Trúc Mai** | `sections/s0_background/s0b_preliminaries.py` |
| 1 | Vấn đề cốt lõi của GNN–LLM fusion trên TAG | **Trúc Mai** | `sections/s1_trucmai/s1_trucmai.py` |
| 2 | Đánh giá các routing heuristic hiện có | **Hoàng Phan** | `sections/s2_hoangphan/s2_hoangphan.py` |
| 3 | Structural signal — local homophily & relative degree | **Nhựt Anh** | `sections/s3_nhutanh/s3_nhutanh.py` |
| 4 | Kiến trúc GLANCE | **Trần Nguyên** | `sections/s4_trannguyen/s4_trannguyen.py` |
| 5 | Training objective & kết quả thực nghiệm | **Thiên Lâm** | `sections/s5_thienlam/s5_thienlam.py` |

> **Ghi chú về Section 0.** Đề bài không gán chủ cho phần Background nên nó được
> tách đôi theo mạch nội dung: 0.1 Related Work đi thẳng vào Task 2 (đánh giá
> heuristic) nên giao Hoàng Phan; 0.2 Preliminaries đi thẳng vào Task 1 (vấn đề
> cốt lõi) nên giao Trúc Mai. Nếu nhóm có người dẫn (lead) muốn tự làm phần 0,
> chỉ cần đổi tên trong bảng này và trong `plan.md` — code không phụ thuộc.

Mỗi người **chỉ sửa file trong folder của mình** + `PLAN.md` của mình.
File dùng chung (`glance_style.py`, `plan.md`, `README.md`, `concat.txt`) phải
báo nhóm trước khi sửa, để tránh conflict.

---

## Cài đặt

Dự án dùng conda env **`graphdm`** (không dùng venv).

```bash
conda activate graphdm
pip install -r requirements.txt
ffmpeg -version      # cần có ffmpeg để ghép video (brew install ffmpeg)
manim checkhealth
```

## Render

Từ thư mục gốc của repo:

```bash
conda activate graphdm

# render 1 scene khi đang code (nhanh, 480p15)
manim -ql sections/s3_nhutanh/s3_nhutanh.py S3_01_Definitions

# render toàn bộ section của mình
manim -ql sections/s3_nhutanh/s3_nhutanh.py

# render toàn bộ video + ghép
./build.sh          # 480p nháp
./build.sh -qh      # 1080p60 bản cuối
```

Lần render đầu cần **mạng** để backend TTS sinh audio; sau đó audio được cache trong
`media/voiceovers/` theo hash của lời thoại nên render lại rất nhanh.

Kết quả: `build/final.mp4` (đã có giọng đọc) + `build/final.srt`.
File `.mp4` từng scene nằm trong `media/videos/<tên_file>/<chất_lượng>/`.

`media/` và `build/` đã được `.gitignore` — **không commit video**.

---

## Quy ước code

1. Mỗi scene là một class, đặt tên `S<số section>_<thứ tự>_<Tên>`, ví dụ
   `S4_02_RoutingFeatures`. Thứ tự số quyết định thứ tự trong video.
2. Kế thừa `GlanceScene` từ `glance_style.py`, không dùng `Scene` trần:

   ```python
   import sys, pathlib
   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
   from glance_style import *

   class S4_01_Overview(GlanceScene):
       section, section_name = "4", "Kiến trúc GLANCE"

       def construct(self):
           self.banner()
           ...
   ```
3. **Thuyết minh tự đồng bộ**: gom lời thoại vào dict `VO` ở đầu file, rồi bọc
   animation trong khối `with self.voiceover(text=VO["..."]) as tracker:`.
   Plugin `manim-voiceover` sinh audio, tự chờ hết câu nói,
   và tự sinh `.srt` — **không** gọi `add_subcaption` nữa (sẽ trùng phụ đề).
   **Giọng đọc chính thức của nhóm là API riêng, tức `GLANCE_TTS=timed`.** Cấu hình
   URL `/api/tts` trong `.env`, đặt bearer key tại `.run/api.key`, và dùng
   `temperature=0.45`, `top_k=30`, `top_p=0.85`, `speed=1.15`. API trả MP3 trực
   tiếp. Các giá trị này có thể cấu hình bằng nhóm biến `GLANCE_TIMED_TTS_*`. Thư mục
   `.run/` đã được Git ignore; không commit key. Bản nộp phải render bằng backend
   này để giọng đồng nhất giữa các section.
   Viết lời thoại theo cách đọc lên: `h_v` → "h của v", `3/4` → "ba phần tư".
   Phiên âm thuật ngữ theo bảng trong `plan.md`, có test gác việc này.

   <details>
   <summary>Backend dự phòng, chỉ dùng khi endpoint của nhóm không chạy</summary>

   Endpoint `timed` được self-host nên có lúc tắt. Khi đó vẫn render thử được bằng
   `GLANCE_TTS=gtts` (miễn phí, cần mạng) hoặc `GLANCE_TTS=record` (tự thu giọng).
   Còn `GLANCE_TTS=azure` cần `pip install "manim-voiceover[azure]>=0.3.7"` và khoá
   `AZURE_*` trong `.env`; nó dùng `en-US-AvaMultilingualNeural`, tự bọc thuật ngữ
   tiếng Anh trong locale `en-US` và phần tiếng Việt trong `vi-VN` để giữ cùng một
   chất giọng khi code-switch. Giọng nam là `GLANCE_VOICE=en-US-AndrewMultilingualNeural`.
   Không dùng Jenny/Ryan Multilingual vì hai voice đó không hỗ trợ `vi-VN`.

   **Đừng dùng các backend này cho bản nộp**: giọng khác hẳn API của nhóm, ghép vào
   sẽ nghe rõ chỗ đổi giọng giữa các section.
   </details>
4. Dùng màu và font từ `glance_style.py` (`C_GNN`, `C_LLM`, `C_ROUTER`, `txt()`,
   `heading()`, `bullets()`...). Không hard-code màu mới.
5. Chữ tiếng Việt: dùng `txt()` / `Text`, **không** dùng `Tex`/`MathTex`
   (LaTeX mặc định không có dấu tiếng Việt). `MathTex` chỉ dùng cho công thức.
6. Mọi số liệu trích từ paper phải kèm `source("Bảng 3, tr.8")` ở góc dưới phải.

## Kiểm tra

```bash
python -m unittest discover -s tests -t .    # cả 9 test
python tests/test_voice_pronunciation.py     # chỉ test phiên âm, không cần manim
```

`test_voice_pronunciation.py` chỉ dùng thư viện chuẩn nên chạy được ở bất cứ đâu. Nó báo lỗi
khi lời thoại còn thuật ngữ tiếng Anh chưa chuyển theo bảng phiên âm trong `plan.md`, và quét
**mọi** cách viết lời thoại: dict `VO`, `voiceover(text=...)`, `narrated_caption(...)` và
helper `beat()`. **Chạy test này trước khi mở PR.**

### Phiên âm lời thoại

Toàn bộ lời thoại hiện đã đưa nợ phiên âm về 0. Test sẽ đỏ ngay nếu một chuỗi TTS
mới chứa lại thuật ngữ tiếng Anh chưa chuyển theo bảng trong `plan.md`.

CI ở `.github/workflows/ci.yml` chạy hai job cho mỗi push và pull request vào `main`: job
*Nội dung và cú pháp* không cài manim nên xong trong vài chục giây, job *Hạ tầng giọng đọc*
cài cả manim để chạy trọn bộ test.

## Quy ước git

```bash
git checkout -b section/<tên-bạn>      # ví dụ: section/nhut-anh
# ... code, commit nhỏ và thường xuyên ...
git push -u origin section/<tên-bạn>
# mở Pull Request vào main
```

Không commit trực tiếp lên `main`. Không commit `media/`, `build/`, `*.mp4`.

---

## Tài liệu

- `plan.md` — kịch bản tổng (mạch phim, thời lượng, màu, motif dùng chung).
- `sections/*/TASK.md` — **đặc tả nhiệm vụ từng section**: phải trình bày ý gì,
  lấy số liệu nào ở đâu, kết bằng câu nào, checklist nộp.
- `sections/_template.py` — khung khởi tạo, copy vào folder của mình rồi viết tiếp.
- `.claude/skills/glance-video/SKILL.md` — hướng dẫn cho AI agent (Claude Code…)
  làm việc trong repo này: quy ước code, cách render, cách tự kiểm tra kết quả.
- `docs/paper-map.md` — bản đồ paper: mục nào của paper thuộc section nào.
- `../GraphDataMining.pdf` — bản PDF của paper.
