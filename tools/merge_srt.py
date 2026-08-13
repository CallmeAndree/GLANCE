"""Ghép các file .srt của từng scene thành một file phụ đề cho video đã stitch.

Manim sinh <Scene>.srt cạnh <Scene>.mp4. Khi nối video, mốc thời gian của scene
sau phải cộng thêm tổng thời lượng các scene trước.

    python tools/merge_srt.py build/concat.txt build/final.srt
"""

import re
import subprocess
import sys
from pathlib import Path

TIME = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
)


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def to_seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def to_stamp(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main(concat_file, out_file):
    concat = Path(concat_file)
    root = concat.parent
    clips = []
    for line in concat.read_text().splitlines():
        line = line.strip()
        if line.startswith("file "):
            clips.append((root / line[5:].strip().strip("'\"")).resolve())

    repo = concat.parent.parent

    def find_srt(mp4):
        """Phụ đề nằm cạnh file manim gốc. Clip đã chuẩn hoá (build/norm/) thì
        phải lần ngược về media/videos/ để lấy .srt."""
        sibling = mp4.with_suffix(".srt")
        if sibling.exists():
            return sibling
        return next(repo.glob(f"media/videos/*/*/{mp4.stem}.srt"), None)

    blocks, offset, index = [], 0.0, 0
    for mp4 in clips:
        clip_len = duration(mp4)
        srt = find_srt(mp4)
        if srt is not None:
            raw = srt.read_text(encoding="utf-8").strip()
            for chunk in re.split(r"\n\s*\n", raw):
                lines = [l for l in chunk.splitlines() if l.strip()]
                if len(lines) < 2:
                    continue
                m = TIME.search(chunk)
                if not m:
                    continue
                # Manim đôi khi ghi thời điểm kết thúc vượt quá độ dài scene;
                # cắt lại để phụ đề không đè sang scene sau.
                start = min(to_seconds(*m.group(1, 2, 3, 4)), clip_len) + offset
                end = min(to_seconds(*m.group(5, 6, 7, 8)), clip_len) + offset
                text = "\n".join(lines[2:]) if TIME.search(lines[0]) is None else "\n".join(lines[1:])
                index += 1
                blocks.append(f"{index}\n{to_stamp(start)} --> {to_stamp(end)}\n{text}")
        offset += duration(mp4)

    if not blocks:
        print("No scene SRT files found; skipping subtitle merge.")
        return
    Path(out_file).write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"Wrote {out_file} ({index} subtitle cues)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
