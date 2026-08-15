#!/usr/bin/env python3
"""Tìm những câu TTS bị đọc méo, dựa trên tốc độ đọc.

    python tools/audit_tts.py                # 25 câu đáng ngờ nhất
    python tools/audit_tts.py --limit 60
    python tools/audit_tts.py --check "một câu cụ thể"

Model TTS khi vấp một cụm chữ cái (ví dụ "lờ lờ mờ, gờ nờ nờ") thì không báo
lỗi — nó kéo dài âm, lặp âm, hoặc lầm bầm cho hết câu. Nghe thì rõ ngay, nhưng
không ai nghe lại được 421 clip.

Dấu vết đo được là **tốc độ đọc**: câu méo bao giờ cũng dài hơn nhiều so với số
âm tiết của nó. Tiếng Việt gần như mỗi tiếng một âm tiết, nên số âm tiết đếm
bằng số tiếng, và âm-tiết-trên-giây của một câu đọc bình thường bám khá sát nhau.
Câu nào tụt hẳn xuống dưới phần còn lại là câu cần nghe lại.

Đây là bộ lọc, không phải toà án: nó thu 421 clip xuống còn vài chục clip đáng
nghe. Câu ngắn (dưới `--min-syllables`) bị bỏ qua vì tỉ lệ của chúng dao động
quá mạnh để so.
"""

import argparse
import json
import pathlib
import re
import statistics
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "media/voiceovers"


def syllables(text: str) -> int:
    """Số âm tiết ~ số tiếng. Bỏ dấu câu, gộp khoảng trắng."""
    return len([w for w in re.sub(r"[^\w\s]", " ", text).split() if w])


def duration(path: pathlib.Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except (subprocess.CalledProcessError, ValueError):
        return None


def collect(cache_dir: pathlib.Path):
    cache = json.loads((cache_dir / "cache.json").read_text(encoding="utf-8"))
    rows, seen = [], set()
    for entry in cache:
        data = entry.get("input_data", {})
        if data.get("service") != "glance-timed-tts-v2":
            continue
        text = data.get("input_text", "")
        if text in seen:
            continue
        seen.add(text)
        audio = cache_dir / entry["original_audio"]
        dur = duration(audio) if audio.is_file() else None
        if not dur:
            continue
        syl = syllables(text)
        rows.append({"text": text, "audio": entry["original_audio"],
                     "dur": dur, "syl": syl, "rate": syl / dur})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", type=pathlib.Path, default=CACHE_DIR)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--min-syllables", type=int, default=6)
    ap.add_argument("--check", action="append", default=[],
                    help="in chỉ số của đúng câu này (so với phân bố chung)")
    args = ap.parse_args()

    rows = collect(args.cache)
    if not rows:
        sys.exit("Không đọc được clip nào từ cache.")

    usable = [r for r in rows if r["syl"] >= args.min_syllables]
    rates = [r["rate"] for r in usable]
    mean, sd = statistics.mean(rates), statistics.pstdev(rates)
    print(f"{len(rows)} clip ({len(usable)} clip từ {args.min_syllables} âm tiết trở lên)")
    print(f"tốc độ đọc: trung bình {mean:.2f} âm tiết/giây, độ lệch chuẩn {sd:.2f}")
    print(f"ngưỡng đáng ngờ: dưới {mean - 2*sd:.2f} âm tiết/giây\n")

    for r in usable:
        r["z"] = (r["rate"] - mean) / sd if sd else 0.0

    if args.check:
        for needle in args.check:
            hit = [r for r in rows if needle.lower() in r["text"].lower()]
            if not hit:
                print(f"  (không thấy câu chứa: {needle!r})")
            for r in hit:
                z = (r["rate"] - mean) / sd if sd else 0.0
                flag = "  <-- ĐÁNG NGỜ" if z < -2 else ""
                print(f"  {r['rate']:5.2f} âm tiết/s  z={z:+5.2f}  "
                      f"{r['dur']:5.2f}s/{r['syl']:3d} tiếng{flag}")
                print(f"      {r['text'][:88]}")
        return

    flagged = sorted(usable, key=lambda r: r["rate"])[: args.limit]
    print(f"{'tốc độ':>7} {'z':>6} {'giây':>6} {'tiếng':>6}  câu")
    for r in flagged:
        print(f"{r['rate']:7.2f} {r['z']:+6.2f} {r['dur']:6.2f} {r['syl']:6d}  "
              f"{r['text'][:76]}")
    n_bad = sum(1 for r in usable if r["z"] < -2)
    print(f"\n{n_bad} clip dưới ngưỡng hai độ lệch chuẩn.")


if __name__ == "__main__":
    main()
