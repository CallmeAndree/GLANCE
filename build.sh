#!/usr/bin/env bash
# Render every section in video order, then stitch into build/final.mp4
#
#   ./build.sh          # 480p15 nháp (mặc định)
#   ./build.sh -qh      # 1080p60 bản cuối
#
# Yêu cầu: conda activate graphdm && pip install -r requirements.txt

set -euo pipefail
cd "$(dirname "$0")"

QUALITY="${1:--ql}"
case "$QUALITY" in
  -ql) RES="480p15" ;;
  -qm) RES="720p30" ;;
  -qh) RES="1080p60" ;;
  -qk) RES="2160p60" ;;
  *) echo "Quality không hợp lệ: $QUALITY (dùng -ql | -qm | -qh | -qk)"; exit 1 ;;
esac

# Thứ tự section trong video. Thêm section mới thì thêm vào đây.
SECTIONS=(
  "sections/s0_background/s0a_related_work.py"
  "sections/s0_background/s0b_preliminaries.py"
  "sections/s1_trucmai/s1_trucmai.py"
  "sections/s2_hoangphan/s2_hoangphan.py"
  "sections/s3_nhutanh/s3_nhutanh.py"
  "sections/s4_trannguyen/s4_trannguyen.py"
  "sections/s5_thienlam/s5_thienlam.py"
)

command -v manim >/dev/null || { echo "Không tìm thấy manim. Chạy: conda activate graphdm"; exit 1; }
command -v ffmpeg >/dev/null || { echo "Không tìm thấy ffmpeg (brew install ffmpeg)"; exit 1; }

mkdir -p build
: > build/concat.txt

for f in "${SECTIONS[@]}"; do
  [ -f "$f" ] || { echo "!! Thiếu file $f — bỏ qua"; continue; }
  echo "==> render $f"
  manim "$QUALITY" -a "$f"

  stem="$(basename "$f" .py)"
  # Lấy tên scene theo đúng thứ tự khai báo trong file
  grep -oE '^class ([A-Za-z0-9_]+)\(' "$f" | sed -E 's/^class //; s/\($//' | while read -r scene; do
    mp4="media/videos/${stem}/${RES}/${scene}.mp4"
    if [ -f "$mp4" ]; then
      echo "file '../${mp4}'" >> build/concat.txt
    else
      echo "!! Thiếu output $mp4"
    fi
  done
done

echo "==> ghép video"
ffmpeg -y -loglevel error -f concat -safe 0 -i build/concat.txt -c copy build/final.mp4

echo "==> ghép phụ đề"
python tools/merge_srt.py build/concat.txt build/final.srt || echo "(bỏ qua phụ đề)"

echo "==> đóng gói softsub (MKV)"
ffmpeg -y -loglevel error -i build/final.mp4 -i build/final.srt -c copy -c:s srt build/final.mkv || echo "(lỗi tạo mkv)"

echo
echo "Xong: build/final.mkv (kèm softsub) và build/final.mp4"
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 build/final.mp4 \
  | awk '{printf "Thời lượng: %d:%02d\n", $1/60, $1%60}'
