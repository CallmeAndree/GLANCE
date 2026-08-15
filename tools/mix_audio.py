#!/usr/bin/env python3
"""Trộn nhạc nền + sound effect vào bản video đã ghép.

    python tools/mix_audio.py                       # dùng mặc định trong build/
    python tools/mix_audio.py --bgm media/audio/x.mp3
    python tools/mix_audio.py --dry-run             # chỉ in bảng mốc SFX

Chạy SAU khi `build.sh` đã ghép xong `build/final.mp4`, và chỉ đụng tới track
audio: video được `-c:v copy` nên bước này mất vài chục giây chứ không render
lại hình.

Vì sao mix ở đây mà không dùng `self.add_sound()` trong từng scene:

  1. Nhạc nền phải chạy liền mạch xuyên suốt video. Gắn theo scene thì mỗi
     scene một đoạn nhạc riêng, đứt ở mọi điểm cắt.
  2. Tiếng chuyển cảnh cần biết mốc cắt GIỮA hai scene — thông tin đó chỉ tồn
     tại ở bước ghép, không scene nào tự biết.
  3. Không phải sửa file của section nào cả.

Ba lớp tiếng, mỗi lớp một vai:

  - Nhạc nền: ducking bằng sidechain, tự hạ xuống khi có giọng đọc rồi lên lại
    ở khoảng lặng. Không có ducking thì nhạc đè lên giọng TTS vốn đã mỏng.
  - Whoosh chuyển cảnh: đặt LỆCH TRƯỚC mốc cắt, xem `LEAD`.
  - Mốc đổi section: whoosh dày hơn + một cú thump trầm, đánh dấu sang chương.

Toàn bộ SFX được tổng hợp tại chỗ bằng numpy — không tải file ngoài, không
vướng bản quyền. Muốn thay bằng tiếng riêng thì bỏ file .wav 48kHz vào
`assets/sfx/` với đúng tên (`whoosh.wav`, `whoosh_section.wav`, `sting.wav`),
script sẽ ưu tiên dùng file đó.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

import sfx_kit
from sfx_kit import SR

# --- Cân bằng âm lượng ------------------------------------------------------
# Mọi mức đều tính TƯƠNG ĐỐI so với độ to trung bình của giọng đọc, đo bằng
# volumedetect ngay lúc chạy. Hardcode một con số tuyệt đối sẽ sai ngay khi đổi
# backend TTS, vì mỗi giọng một mức ra khác nhau.
BGM_BELOW_VOICE = 12.0     # dB — nhạc nền nằm dưới giọng đọc chừng này

# Whoosh nào đặt ở đâu. Trước đây script rải whoosh lên TOÀN BỘ 58 mốc cắt, tức
# là cứ vài chục giây lại một tiếng gió — nghe thành tic của video chứ không còn
# là dấu chuyển ý. Giờ chỉ hai nhóm:
#
#   * Đổi section: tự nhận ra qua tiền tố S1_/S2_… nên không phải liệt kê.
#   * Chuyển cảnh LỚN: liệt kê đích danh dưới đây, theo TÊN SCENE.
#
# Neo theo tên scene chứ không theo mốc giây: mỗi lần sinh lại một câu TTS là
# toàn bộ timeline phía sau dịch đi, bảng mốc tuyệt đối sẽ sai ngay lần sau.
# Accent ngữ nghĩa (tick, ping, pulse…) KHÔNG đặt ở đây mà gọi `self.sfx(...)`
# ngay trong scene, xem GlanceScene.sfx.
MAJOR_TRANSITIONS = {
    "S2_08_Table1",            # bảng kết quả đầu tiên hiện lên
    "S2_12_Limits",            # chốt ba hạn chế, đổi giọng lập luận
    "S3_06_FiveSignals",       # chuyển từ phát hiện tín hiệu sang xây feature
    "S3_12_NodeEmbedding",     # bắt đầu đi qua từng tín hiệu một
    "S4_15_RouterScore",       # vào phần router
    "S4_23_EgoEmbedding",      # vào phần ba mức ngữ cảnh của LLM
    "S5_06_Setup",             # chuyển từ huấn luyện sang thực nghiệm
    "S5_11_Callout",           # đoạn kết
}

# Độ sâu ducking phải đi kèm BGM_BELOW_VOICE, không chỉnh rời. Nhạc càng to thì
# càng phải hạ sâu lúc có giọng, nếu không lời đọc bị lấn: mục tiêu là khoảng
# lặng nghe đầy hơn, còn mức nhạc DƯỚI lời thoại thì giữ gần như cũ.
DUCK_RATIO = 12            # càng lớn càng hạ sâu
DUCK_THRESHOLD = 0.03      # biên độ giọng đọc bắt đầu kích hoạt nén
DUCK_RELEASE = 450         # ms — dài để nhạc không phập phồng giữa các câu

# --- Nhịp -------------------------------------------------------------------
# Whoosh phải CHỚM TRƯỚC điểm cắt thì mới nghe như nó đẩy cảnh đi; đặt đúng
# ngay mốc cắt sẽ thành ra phản ứng chậm nửa nhịp. GlanceScene.tear_down() để
# lại 0.5s tĩnh cuối mỗi scene, nên khoảng lệch này rơi trọn vào chỗ im lặng.
LEAD = 0.30                # giây — whoosh bắt đầu trước mốc cắt
STING_AT = 0.35            # giây — tiếng mở đầu, sau khi title card hiện
FADE_IN = 2.5              # giây — nhạc vào
FADE_OUT = 6.0             # giây — nhạc ra


# ---------------------------------------------------------------------------
# Mốc thời gian
# ---------------------------------------------------------------------------
def ffprobe_duration(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def mean_volume(path: pathlib.Path, start: float = 0.0, dur: float | None = None) -> float:
    """Độ to trung bình (dBFS) qua volumedetect — dùng để cân nhạc với giọng."""
    # Không hạ loglevel: volumedetect in kết quả ở mức `info`, đặt `-v error`
    # là mất luôn con số cần đọc.
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start:
        cmd += ["-ss", str(start)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", err)
    if not m:
        sys.exit(f"Không đọc được mean_volume của {path}")
    return float(m.group(1))


def scene_marks(concat: pathlib.Path) -> list[tuple[float, str, str]]:
    """Trả (mốc cắt, tên scene sắp vào, loại tiếng) cho những mốc ĐÁNG đánh dấu.

    Chỉ hai loại lọt qua: mốc đổi section, và các chuyển cảnh lớn liệt kê trong
    `MAJOR_TRANSITIONS`. Mọi mốc cắt còn lại không có tiếng — rải whoosh lên cả
    58 mốc thì nó thành tiếng nền đều đặn, mất hẳn ý nghĩa báo chuyển ý.

    Bỏ qua mốc 0 (đầu video, đã có sting riêng) và mốc cuối.
    """
    entries = []
    for line in concat.read_text().splitlines():
        m = re.match(r"file '(.+)'$", line.strip())
        if m:
            entries.append((concat.parent / m.group(1)).resolve())

    marks, clock, prev_section = [], 0.0, None
    for path in entries:
        name = path.stem
        sec = m.group(1) if (m := re.match(r"S(\d+)_", name)) else "0"
        if clock > 0:
            if sec != prev_section:
                marks.append((clock, name, "section_whoosh"))
            elif name in MAJOR_TRANSITIONS:
                marks.append((clock, name, "whoosh"))
        prev_section = sec
        clock += ffprobe_duration(path)
    return marks


# ---------------------------------------------------------------------------
# Bed SFX
# ---------------------------------------------------------------------------
def write_bed(marks, sfx, total: float, voice_mean: float, out: pathlib.Path) -> None:
    """Rải SFX lên một track im lặng dài bằng video, ghi ra WAV 16-bit.

    Không cấp phát nguyên mảng dài bằng video: 30 phút stereo là 1.4 GB float64
    cho vỏn vẹn vài chục sự kiện dưới một giây. Thay vào đó gom các sự kiện
    chồng lấn thành cụm, rồi ghi xen kẽ im-lặng / cụm.
    """
    def level(kind):
        return voice_mean - sfx_kit.LEVELS[kind]

    events = [(STING_AT, sfx["sting"], level("sting"))]
    for at, _name, kind in marks:
        events.append((at - LEAD, sfx[kind], level(kind)))

    spans = []                          # [start_sample, mảng cụm]
    for at, clip, gain_db in sorted(events, key=lambda e: e[0]):
        start = max(0, int(at * SR))
        data = clip * (10 ** (gain_db / 20.0))
        if spans and start < spans[-1][0] + spans[-1][1].shape[0]:
            # Hai mốc cắt quá gần nhau: nới cụm trước rồi cộng chồng vào.
            off = start - spans[-1][0]
            need = off + data.shape[0] - spans[-1][1].shape[0]
            if need > 0:
                spans[-1][1] = np.vstack([spans[-1][1], np.zeros((need, 2))])
            spans[-1][1][off : off + data.shape[0]] += data
        else:
            spans.append([start, data])

    peak = max((np.max(np.abs(d)) for _, d in spans), default=0.0)
    scale = 0.99 / peak if peak > 0.99 else 1.0   # chỉ chạm tới khi SFX chồng nhau

    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        cursor = 0
        for start, data in spans:
            w.writeframes(b"\0" * ((start - cursor) * 4))
            w.writeframes((data * scale * 32767).astype("<i2").tobytes())
            cursor = start + data.shape[0]
        w.writeframes(b"\0" * (max(0, int(total * SR) - cursor) * 4))


# ---------------------------------------------------------------------------
def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", type=pathlib.Path, default=root / "build/final.mp4")
    ap.add_argument("--concat", type=pathlib.Path, default=root / "build/concat.txt")
    ap.add_argument("--bgm", type=pathlib.Path, default=root / "media/audio/dl.mp3")
    ap.add_argument("--assets", type=pathlib.Path, default=root / "assets/sfx")
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="mặc định: ghi đè chính --video")
    ap.add_argument("--no-sfx", action="store_true", help="chỉ nhạc nền")
    ap.add_argument("--no-bgm", action="store_true", help="chỉ sound effect")
    ap.add_argument("--dry-run", action="store_true", help="in mốc SFX rồi thoát")
    args = ap.parse_args()

    if not args.video.is_file():
        sys.exit(f"Không thấy {args.video} — chạy ./build.sh trước.")
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"Không tìm thấy {tool} (brew install ffmpeg)")

    out = args.out or args.video
    total = ffprobe_duration(args.video)

    marks = []
    if not args.no_sfx:
        if args.concat.is_file():
            marks = scene_marks(args.concat)
        else:
            print(f"!! Không thấy {args.concat} — bỏ qua sound effect chuyển cảnh")

    if args.dry_run:
        print(f"Video {total/60:.1f} phút, {len(marks)} mốc có tiếng chuyển cảnh")
        for at, name, kind in marks:
            print(f"  {int(at)//60:>3}:{at%60:05.2f}  {kind:<15} {name}")
        return

    voice_mean = mean_volume(args.video)
    print(f"Giọng đọc trung bình {voice_mean:.1f} dBFS")

    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="glance-mix-"))
    try:
        inputs, chains, mixes = ["-i", str(args.video)], [], ["[voc]"]
        idx = 1

        if not args.no_bgm and not args.bgm.is_file():
            # media/ nằm trong .gitignore nên máy vừa clone về sẽ không có file
            # nhạc. Báo rõ rồi vẫn trộn tiếp phần SFX, đừng làm hỏng cả build.
            print(f"!! Không thấy nhạc nền {args.bgm} — chỉ trộn sound effect")

        if not args.no_bgm and args.bgm.is_file():
            # Đo giữa bài chứ không đo từ đầu: nhiều bản nhạc mở bằng đoạn intro
            # nhỏ tiếng, lấy đó làm chuẩn thì phần thân sẽ to lố.
            bgm_dur = ffprobe_duration(args.bgm)
            bgm_mean = mean_volume(args.bgm, start=min(120.0, bgm_dur / 3), dur=180.0)
            gain = (voice_mean - BGM_BELOW_VOICE) - bgm_mean
            print(f"Nhạc nền {args.bgm.name}: {bgm_mean:.1f} dBFS → chỉnh {gain:+.1f} dB")

            inputs += ["-stream_loop", "-1", "-i", str(args.bgm)]
            chains.append(
                f"[{idx}:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,"
                f"atrim=0:{total:.3f},asetpts=N/SR/TB,volume={gain:.2f}dB,"
                f"afade=t=in:st=0:d={FADE_IN},"
                f"afade=t=out:st={max(0.0, total - FADE_OUT):.3f}:d={FADE_OUT}[bg]"
            )
            # Nén sidechain: nhạc là tín hiệu bị nén, giọng đọc là tín hiệu điều
            # khiển.
            chains.append(
                f"[bg][sc]sidechaincompress=threshold={DUCK_THRESHOLD}:"
                f"ratio={DUCK_RATIO}:attack=5:release={DUCK_RELEASE}:makeup=1[bgduck]"
            )
            mixes.append("[bgduck]")
            idx += 1

        if marks:
            bed = tmpdir / "sfx_bed.wav"
            kit = {k: sfx_kit.load(k, args.assets)
                   for k in ("sting", "whoosh", "section_whoosh")}
            write_bed(marks, kit, total, voice_mean, bed)
            n_sec = sum(1 for _, _, k in marks if k == "section_whoosh")
            print(f"SFX chuyển cảnh: {n_sec} mốc đổi section + "
                  f"{len(marks) - n_sec} chuyển cảnh lớn + 1 tiếng mở đầu")
            inputs += ["-i", str(bed)]
            chains.append(f"[{idx}:a]aformat=sample_fmts=fltp:sample_rates={SR}:"
                          f"channel_layouts=stereo[sfx]")
            mixes.append("[sfx]")
            idx += 1

        if len(mixes) == 1:
            sys.exit("Không có gì để trộn (đã tắt cả nhạc nền lẫn SFX).")

        split = "asplit=2[voc][sc]" if any("[sc]" in c for c in chains) else "anull[voc]"
        chains.insert(0, f"[0:a]aformat=sample_fmts=fltp:sample_rates={SR}:"
                         f"channel_layouts=stereo,{split}")
        # normalize=0 là bắt buộc: mặc định amix chia đều biên độ cho số input,
        # tức là thêm nhạc nền sẽ tự động làm giọng đọc nhỏ đi một nửa.
        chains.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0:"
                      f"duration=first[aout]")

        tmp_out = tmpdir / "mixed.mp4"
        cmd = (["ffmpeg", "-y", "-v", "error", "-stats", *inputs,
                "-filter_complex", ";".join(chains),
                "-map", "0:v:0", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
                "-movflags", "+faststart", str(tmp_out)])
        print("==> trộn audio")
        subprocess.run(cmd, check=True)

        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_out), str(out))
        print(f"Xong: {out}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
