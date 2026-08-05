---
name: glance-video
description: Hướng dẫn làm việc trong repo video GLANCE — cấu trúc repo, quy ước viết scene Manim, cách render một scene / một section / cả video, cách ghép phụ đề, và cách kiểm tra kết quả. Dùng skill này BẤT CỨ KHI NÀO được yêu cầu viết, sửa, render, debug hoặc review nội dung video trong repo này (bất kỳ file nào trong sections/, glance_style.py, build.sh, tools/).
---

# Làm việc trong repo video GLANCE

Repo này dựng một video giải thích paper **GLANCE** (arXiv:2510.10849) bằng
**Manim Community Edition**. Video chia thành 6 section; mỗi section do một
thành viên sở hữu và render thành `.mp4` riêng, rồi `ffmpeg` ghép lại.

## Quy tắc bắt buộc trước khi làm bất cứ việc gì

1. **Đọc `sections/<folder>/TASK.md` của section liên quan trước khi viết code.**
   File đó là đặc tả nội dung: phải trình bày ý gì, lấy số liệu nào, kết bằng câu
   cầu nối nào. Không tự nghĩ ra nội dung ngoài đặc tả.
2. **Không sửa file của section khác.** Mỗi người một folder. File dùng chung
   (`glance_style.py`, `plan.md`, `README.md`, `build.sh`) chỉ sửa khi được yêu
   cầu rõ ràng, vì mọi section phụ thuộc vào chúng.
3. **Không bịa số liệu.** Mọi con số phải lấy từ `docs/paper-map.md` (đã trích sẵn
   kèm số bảng, số trang) hoặc từ `../GraphDataMining.pdf`. Số liệu nào lên hình
   cũng phải kèm `source("Bảng 3, tr.8")`.
4. **Không commit video.** `media/`, `build/`, `*.mp4` đã nằm trong `.gitignore`.

## Môi trường

Dự án dùng **conda env `graphdm`**, không dùng venv.

```bash
conda activate graphdm
python -c "import manim; print(manim.__version__)"   # cần >= 0.19
ffmpeg -version                                       # cần cho việc ghép video
```

Nếu thiếu: `pip install -r requirements.txt`. `MathTex`/`Tex` cần LaTeX (macOS:
MacTeX, kiểm tra bằng `which latex`).
Code-switch Azure cần thêm `pip install "manim-voiceover[azure]>=0.3.7"`.

Trong môi trường không interactive, gọi thẳng binary để chắc chắn đúng env:
`~/miniconda3/envs/graphdm/bin/manim ...`

## Cấu trúc repo

```
glance_style.py            # ngôn ngữ hình ảnh dùng chung — ĐỌC TRƯỚC KHI VIẾT SCENE
manim.cfg                  # media_dir + màu nền, áp cho mọi lần render
plan.md                    # kịch bản tổng: thứ tự section, thời lượng, câu cầu nối, bảng màu
docs/paper-map.md          # mục paper → section, và toàn bộ số liệu đã trích sẵn
sections/_template.py      # khung khởi tạo cho một section mới
sections/<sX_ten>/         # một folder một người
    TASK.md                # đặc tả nội dung section đó
    <sX_ten>.py            # code Manim của section đó
build.sh                   # render tất cả + ghép thành build/final.mp4
tools/merge_srt.py         # ghép các .srt của từng scene, dịch mốc thời gian
media/                     # output manim (gitignored)
build/                     # final.mp4, final.srt, concat.txt (gitignored)
```

## Quy ước viết scene

Mỗi file section bắt đầu bằng bootstrap import rồi khai báo metadata:

```python
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from glance_style import *

SECTION, SECTION_NAME, OWNER = "3", "Structural signal", "Nhựt Anh"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)


class S3_02_Stratified(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        ...
```

Bắt buộc:

- **Tên class**: `S<số section>_<số thứ tự 2 chữ số>_<TênNgắn>`, ví dụ `S4_03_Router`.
  `build.sh` ghép video **theo đúng thứ tự class khai báo trong file** — muốn đổi
  thứ tự thì đổi vị trí class, không đổi tên.
- **Kế thừa `GlanceScene`**, không dùng `Scene` trần. `GlanceScene` lo màu nền,
  banner section, và các tiện ích `self.banner()`, `self.say()`, `self.clear_scene()`.
- **Mọi animation nằm trong khối thuyết minh** (xem mục "Thuyết minh" bên dưới).
  Không gọi `add_subcaption` / tham số `subcaption` nữa — plugin tự sinh phụ đề
  từ chính text thuyết minh, gọi thêm sẽ bị trùng dòng.
- **Tiếng Việt dùng `txt()` / `Text`**, tuyệt đối không dùng `Tex`/`MathTex` cho
  tiếng Việt (LaTeX mặc định không có dấu). `MathTex` chỉ dùng cho công thức toán.
- **Chỉ dùng màu và helper trong `glance_style.py`.** Không hard-code mã màu mới,
  không tự vẽ lại dấu ✓/✗ hay khối model.

## Thuyết minh (manim-voiceover)

Video có giọng đọc tự sinh. `GlanceScene` kế thừa `VoiceoverScene` và tự gắn TTS
trong `setup()`, nên trong scene chỉ cần bọc animation:

```python
VO = {"intro": "Tín hiệu đầu tiên là local homophily."}

with self.voiceover(text=VO["intro"]) as tracker:
    self.play(Write(head), run_time=1.6)
    self.play(GrowFromCenter(v_dot), run_time=1.2)
    # animation ngắn hơn lời đọc -> khối tự chờ nốt phần audio còn thừa
    # cần một animation dài đúng bằng câu nói -> run_time=tracker.duration
```

Quy tắc:

- **Gom lời thuyết minh vào dict `VO` ở đầu file**, không rải chuỗi trong code —
  dễ duyệt kịch bản và dễ sửa.
- **Viết theo cách đọc lên, không theo cách viết công thức**: `h_v` → "h của v",
  `3/4` → "ba phần tư", `0.75` → "không phẩy bảy lăm", `N(v)` → "tập hàng xóm của v".
  TTS đọc ký hiệu toán rất tệ.
- **Lời `VO` không để tiếng Anh cho model tự đoán cách đọc.** Chữ trên hình vẫn giữ
  thuật ngữ gốc, nhưng lời đọc dùng phiên âm đã chốt (`node` → "nót") và ưu tiên
  tiếng Việt tự nhiên cho từ còn lại (`routing` → "định tuyến", `embedding` →
  "véc-tơ biểu diễn"). Acronym dùng đúng
  bảng phiên âm chung: `LLM` → "eo eo em", `MLP Q` → "em eo pi khiu",
  `GNN` → "gi en en", `GLANCE` → "gờ lans".
- Đừng để tổng `run_time` trong khối vượt quá độ dài lời đọc, nếu không hình sẽ
  chạy lố sang câu sau. Kiểm tra bằng cách so `tracker.duration` với tổng run_time.
- Audio **cache theo hash của text** trong `media/voiceovers/`. Sửa animation thì
  không gọi lại TTS; sửa text thì mới sinh lại. Đừng commit thư mục này.
- `self.say("...")` cho nhịp chỉ có lời đọc, không animation.
- `self.pad_to(t)` chỉ dùng khi kịch bản ép mốc giây tuyệt đối; bình thường để
  audio quyết định nhịp.

**Đổi giọng đọc bằng biến môi trường, không sửa code section:**

| Lệnh | Service | Khi nào dùng |
|---|---|---|
| `GLANCE_TTS=timed manim ...` | Timed API | mặc định — cần `GLANCE_TIMED_TTS_URL` + `GLANCE_TIMED_TTS_TOKEN` trong `.env`, trả MP3 và timing từng segment |
| `GLANCE_TTS=gtts manim ...` | gTTS `vi` | dự phòng — free, cần mạng, giọng hơi máy |
| `GLANCE_TTS=azure manim ...` | Azure `en-US-AvaMultilingualNeural` | bản nộp — tự code-switch Việt-Anh, cần `AZURE_SUBSCRIPTION_KEY` + `AZURE_SERVICE_REGION` trong `.env` |
| `GLANCE_TTS=record manim ...` | RecorderService | thu giọng thật qua CLI lúc render (`brew install sox`) |

Timed API và gTTS cần mạng khi render lời thoại mới; audio đã sinh được cache theo
text + backend trong `media/voiceovers/`. Không commit token timed API.
Với Azure, `GlanceScene` tự bọc các thuật ngữ trong `EN_TERMS` và acronym trong
`EN_ACRONYMS` bằng locale `en-US`; phần còn lại dùng `vi-VN`. Đổi sang giọng nam
bằng `GLANCE_VOICE=en-US-AndrewMultilingualNeural`. Có thể dùng bản HD Ava/Andrew
`DragonHDLatestNeural`. Không dùng `JennyMultilingualNeural` hoặc
`RyanMultilingualNeural` vì hai voice này không hỗ trợ `vi-VN` và có thể sinh
audio rỗng. Thêm thuật ngữ đọc sai vào danh sách dùng chung trong
`glance_style.py`, không chèn SSML thủ công vào từng section.

## API của `glance_style.py`

Text: `txt(s, size, color)` · `mono(s)` · `heading(s, color)` · `bullets([...])` ·
`caption(s)` · `source(ref)` (stamp nguồn góc dưới phải)

Bố cục: `title_card(title, subtitle, owner, accent)` · `section_banner(num, name)` ·
`panel(mobj)` (khung bo góc) · `labeled_box("GNN", C_GNN)` ·
`pipeline([(label, color), ...])` (chuỗi khối + mũi tên) · `check()` · `cross()`

Đồ thị: `tag_graph(edges, positions, labels)` trả VGroup có `.nodes` (dict id → Dot)
và `.edges` · `demo_tag()` — **đồ thị 12 node dùng chung cả video**, node 4 là hub
homophily cao, node 9 là node homophily thấp; section 0.2/1/3/4 phải dùng lại đúng
đồ thị này để khán giả nhận ra · `ego_ring(graph, id, hop_ids)` · `text_chip("...")`

Biểu đồ: `bar_chart(values, labels, colors, y_range, value_fmt)` — hỗ trợ giá trị âm
(cần cho NCS ở section 2).

Màu (ý nghĩa cố định toàn video): `C_GNN` teal · `C_LLM` amber · `C_ROUTER` tím ·
`C_GOOD` xanh lá · `C_BAD` đỏ · `C_EDGE` cạnh đồ thị · `C_HIGHLIGHT` xanh dương ·
`INK` chữ chính · `MUTED` chữ phụ · `BG` nền.

Cần helper mới thì **thêm vào `glance_style.py`**, không copy code vào folder section.

## Render và build

```bash
conda activate graphdm

# 1 scene khi đang code — nhanh nhất
manim -ql sections/s3_nhutanh/s3_nhutanh.py S3_02_Stratified

# cả section
manim -ql sections/s3_nhutanh/s3_nhutanh.py -a

# cả video: render mọi section theo thứ tự trong build.sh rồi ghép
./build.sh          # 480p15 nháp
./build.sh -qh      # 1080p60 bản cuối
```

Cờ chất lượng: `-ql` 480p15 (mặc định khi làm việc) · `-qm` 720p30 · `-qh` 1080p60 ·
`-qk` 4K. **Luôn dùng `-ql` khi đang lặp**, chỉ `-qh` khi xuất bản cuối.

Output: `media/videos/<tên_file_py>/<độ_phân_giải>/<TênScene>.mp4` (+ `.srt` cùng chỗ).
`build.sh` ghi `build/concat.txt`, ghép ra `build/final.mp4`, rồi gọi
`tools/merge_srt.py` để dồn phụ đề thành `build/final.srt`.

Thêm section mới thì phải thêm đường dẫn file vào mảng `SECTIONS` trong `build.sh`
đúng vị trí mong muốn trong video.

## Tự kiểm tra kết quả (quan trọng)

Render thành công **không** có nghĩa là hình đúng. Manim không báo lỗi khi chữ tràn
khỏi khung hay hai mobject đè nhau. Sau khi render, luôn trích một frame ra xem:

```bash
S=media/videos/s3_nhutanh/480p15/S3_02_Stratified.mp4
D=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$S")
ffmpeg -y -loglevel error -ss $(python -c "print(max(0,$D-2))") -i "$S" -frames:v 1 /tmp/check.png
```

rồi mở `/tmp/check.png` bằng công cụ đọc ảnh. Kiểm tra: chữ có bị tràn mép không,
có đè lên nhau không, dấu tiếng Việt có hiện đúng không, banner và stamp nguồn có
bị che không.

Kiểm tra thời lượng so với mục tiêu trong `plan.md`:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 build/final.mp4
```

## Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `ModuleNotFoundError: glance_style` | thiếu 2 dòng bootstrap `sys.path` | copy lại từ `sections/_template.py` |
| `ModuleNotFoundError: importlib_metadata` | thiếu dependency của manim | `pip install importlib_metadata` |
| Chữ tiếng Việt mất dấu / ra ô vuông | dùng `Tex`/`MathTex` cho tiếng Việt | chuyển sang `txt()` |
| `latex` not found | chưa cài LaTeX | cài MacTeX, hoặc thay `MathTex` bằng `txt()` |
| Chữ tràn khỏi khung | không giới hạn bề rộng | `mobj.scale_to_fit_width(11)` trước khi đặt vị trí |
| Scene thiếu trong `final.mp4` | đổi tên class sau khi render | xoá `media/` rồi render lại |
| Phụ đề hiện hai lần | vừa `voiceover` vừa `add_subcaption` | bỏ `add_subcaption` |
| Hình chạy lố sang câu nói sau | tổng `run_time` > `tracker.duration` | rút bớt animation trong khối |
| gTTS lỗi mạng khi render | không có internet | render lại khi có mạng, hoặc `GLANCE_TTS=record` |
| `SoX could not be found` | chỉ RecorderService mới cần | bỏ qua với gTTS/Azure, hoặc `brew install sox` |
| Video cuối không có tiếng | mở nhầm file scene chưa viết lời | kiểm tra: `ffprobe -select_streams a build/final.mp4` |
| Tiếng lệch dần khỏi hình | audio mỗi scene ngắn hơn video vài chục ms, cộng dồn khi ghép | `build.sh` đã đệm `apad` cho từng clip — đừng ghép tay bằng `-c copy` |
| gTTS lỗi liên tục dù có mạng | bị rate-limit khi sinh nhiều câu mới một lúc | dùng Azure (`.env`), hoặc chạy lại vài lần vì cache tích luỹ dần |
| Các card cao thấp so le | `arrange(RIGHT)` căn theo tâm | thêm `aligned_edge=UP` |

## Khi được yêu cầu viết nội dung một section

1. Đọc `sections/<folder>/TASK.md` — đó là phạm vi công việc, không làm rộng hơn.
2. Đọc `plan.md` để lấy đúng thời lượng mục tiêu và câu cầu nối kết section.
3. Đọc `docs/paper-map.md` để lấy số liệu; cần chi tiết hơn thì đọc
   `../GraphDataMining.pdf` (dùng tham số `pages`, PDF 23 trang).
4. Viết scene, render `-ql`, trích frame ra kiểm tra, sửa cho tới khi bố cục sạch.
5. Báo lại thời lượng thực tế và những chỗ lệch so với đặc tả.
