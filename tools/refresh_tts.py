#!/usr/bin/env python3
"""Sinh lại audio TTS cho những câu chỉ định, bỏ bản cũ trong cache.

    python tools/refresh_tts.py --match "mật độ xê, được kế thừa"
    python tools/refresh_tts.py --match "..." --match "..." --dry-run

Dùng khi một câu bị đọc méo. Model tất định theo câu chữ + tham số, nhưng bản
nằm trong cache có thể được sinh lúc server đang ở trạng thái xấu — đã gặp
trường hợp cùng một câu, bản cache dài 4.53s trong khi sinh lại chỉ 3.42s, tức
bản cũ bị kéo dài gần một phần ba. Xoá entry rồi gọi lại là xong, không phải
sửa lời thoại.

Sau khi chạy, render lại scene chứa câu đó để video lấy audio mới:

    manim -ql sections/s2_hoangphan/s2_hoangphan.py S2_07_NCS

Câu nào sinh lại vẫn méo thì mới phải viết lại lời — lúc đó dùng
`tools/audit_tts.py` để so tốc độ đọc trước và sau.
"""

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CACHE_DIR = ROOT / "media/voiceovers"


def duration(path: pathlib.Path):
    try:
        return float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, check=True).stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match", action="append", required=True,
                    help="chuỗi con của câu cần sinh lại (lặp được)")
    ap.add_argument("--cache", type=pathlib.Path, default=CACHE_DIR)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import glance_style as G

    cache_path = args.cache / "cache.json"
    entries = json.loads(cache_path.read_text(encoding="utf-8"))

    targets = []
    for entry in entries:
        data = entry.get("input_data", {})
        if data.get("service") != "glance-timed-tts-v2":
            continue
        text = data.get("input_text", "")
        if any(m.lower() in text.lower() for m in args.match):
            targets.append(entry)

    if not targets:
        sys.exit("Không thấy câu nào khớp trong cache.")

    print(f"{len(targets)} câu sẽ được sinh lại:")
    for e in targets:
        old = args.cache / e["original_audio"]
        print(f"  {duration(old) or 0:5.2f}s  {e['input_data']['input_text'][:72]}")
    if args.dry_run:
        return

    token = G._read_tts_key(pathlib.Path(ROOT / G.DEFAULT_TIMED_TTS_KEY_FILE))
    service = G.TimedTTSService(endpoint=G.DEFAULT_TIMED_TTS_URL, token=token,
                                cache_dir=str(args.cache))

    # Bỏ entry cũ TRƯỚC khi gọi, nếu không `_wrap_generate_from_text` sẽ trả
    # đúng bản cũ trong cache. File audio cũ để nguyên: entry mới trỏ sang tên
    # file khác, còn giữ bản cũ thì so lại được.
    drop = {id(e) for e in targets}
    kept = [e for e in entries if id(e) not in drop]
    cache_path.write_text(json.dumps(kept, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    ok = 0
    for e in targets:
        text = e["input_data"]["input_text"]
        speed = e["input_data"].get("speed", G.DEFAULT_TIMED_TTS_SPEED)
        try:
            with service.speed_override(speed):
                result = service._wrap_generate_from_text(text)
        except Exception as exc:                      # server tunnel hay chết
            print(f"  LỖI: {text[:56]}… → {exc}")
            continue
        new = args.cache / result["original_audio"]
        old_dur = duration(args.cache / e["original_audio"]) or 0
        new_dur = duration(new) or 0
        delta = f"{new_dur - old_dur:+.2f}s"
        print(f"  {old_dur:5.2f}s → {new_dur:5.2f}s ({delta})  {text[:60]}")
        ok += 1

    print(f"\n{ok}/{len(targets)} câu đã sinh lại. Nhớ render lại scene liên quan.")


if __name__ == "__main__":
    main()
