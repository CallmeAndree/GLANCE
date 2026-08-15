#!/usr/bin/env python3
"""Gỡ `endpoint` khỏi khoá cache TTS trong media/voiceovers/cache.json.

    python tools/migrate_cache_key.py [--dry-run]

Chạy một lần, sau khi `_cache_input_data` thôi đưa endpoint vào khoá. Entry cũ
được ghi kèm endpoint nên khoá mới (không có endpoint) sẽ không khớp được với
chúng — phải gỡ khỏi chính file cache thì audio cũ mới dùng lại được.

Nhân tiện dồn các entry trùng: manim-voiceover 0.3.x ghi lại cả cache sau mỗi
câu, nên file phình ra rất nhiều bản sao y hệt.
"""

import argparse
import json
import pathlib
import shutil
import sys

CACHE = pathlib.Path(__file__).resolve().parents[1] / "media/voiceovers/cache.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=pathlib.Path, default=CACHE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.cache.is_file():
        sys.exit(f"Không thấy {args.cache}")

    entries = json.loads(args.cache.read_text(encoding="utf-8"))
    seen, out, stripped = set(), [], 0
    for entry in entries:
        data = entry.get("input_data", {})
        if "endpoint" in data:
            data.pop("endpoint")
            stripped += 1
        key = json.dumps(data, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)

    print(f"{len(entries)} entry → {len(out)} sau khi gỡ endpoint và dồn trùng "
          f"({stripped} entry có endpoint, {len(entries) - len(out)} bản sao bị bỏ)")

    missing = [e for e in out
               if not (args.cache.parent / e["original_audio"]).is_file()]
    if missing:
        print(f"!! {len(missing)} entry trỏ tới file audio không tồn tại")

    if args.dry_run:
        return

    backup = args.cache.with_suffix(".json.bak")
    shutil.copy2(args.cache, backup)
    tmp = args.cache.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(args.cache)
    print(f"Đã ghi {args.cache} (bản cũ giữ ở {backup.name})")


if __name__ == "__main__":
    main()
