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

mkdir -p build build/norm
: > build/concat.txt

# Chuẩn hoá mọi clip trước khi ghép, vì hai lý do:
#  1. Scene chưa viết lời thuyết minh thì không có audio stream; ghép bằng
#     -c copy đòi mọi clip cùng bố cục stream.
#  2. Manim xuất audio ngắn hơn video vài chục ms mỗi scene. Ghép nối tiếp thì
#     sai số cộng dồn và tiếng lệch dần khỏi hình. Đệm im lặng cho audio dài
#     đúng bằng video (apad + -shortest) để mỗi clip tự khớp.
normalize() {
  local src="$1" dst="build/norm/$(basename "$1")"
  if ffprobe -v error -select_streams a -show_entries stream=codec_type \
       -of csv=p=0 "$src" | grep -q audio; then
    ffmpeg -y -loglevel error -i "$src" \
      -c:v copy -c:a aac -b:a 128k -ar 48000 -ac 2 -af apad -shortest "$dst"
  else
    ffmpeg -y -loglevel error -i "$src" \
      -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
      -shortest -c:v copy -c:a aac -b:a 128k "$dst"
  fi
  printf '%s' "$dst"
}

for f in "${SECTIONS[@]}"; do
  [ -f "$f" ] || { echo "!! Thiếu file $f — bỏ qua"; continue; }
  echo "==> render $f"
  manim "$QUALITY" -a "$f"

  stem="$(basename "$f" .py)"
  # Lấy tên scene theo đúng thứ tự khai báo trong file
  for scene in $(grep -oE '^class ([A-Za-z0-9_]+)\(' "$f" | sed -E 's/^class //; s/\($//'); do
    mp4="media/videos/${stem}/${RES}/${scene}.mp4"
    if [ -f "$mp4" ]; then
      echo "file '../$(normalize "$mp4")'" >> build/concat.txt
    else
      echo "!! Thiếu output $mp4"
    fi
  done
done

echo "==> ghép video"
# Video copy (không mã hoá lại, giữ nguyên chất lượng), nhưng audio phải mã hoá
# lại thành MỘT stream liền mạch: nối AAC bằng -c copy để lại điểm nối có
# priming samples, khiến QuickTime câm tiếng dù ffprobe vẫn thấy track.
ffmpeg -y -loglevel error -f concat -safe 0 -i build/concat.txt \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart build/final.mp4

echo "==> ghép phụ đề"
python tools/merge_srt.py build/concat.txt build/final.srt || echo "(bỏ qua phụ đề)"

echo "==> đóng gói softsub (MKV)"
ffmpeg -y -loglevel error -i build/final.mp4 -i build/final.srt \
  -c copy -c:s srt build/final.mkv || echo "(lỗi tạo mkv)"

# Mỗi lần build tạo một snapshot riêng trong media/videos/<thời điểm>/ để so
# được các bản dựng với nhau. build/final.mp4 luôn là bản mới nhất.
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
SNAP="media/videos/${STAMP}"
mkdir -p "$SNAP"
cp build/final.mp4 "$SNAP/final.mp4"
[ -f build/final.srt ] && cp build/final.srt "$SNAP/final.srt"
cp build/concat.txt "$SNAP/concat.txt"
[ -f build/final.mkv ] && cp build/final.mkv "$SNAP/final.mkv"

DUR="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 build/final.mp4)"
# awk chứ không phải bc: ffprobe trả số thực, bc không làm modulo số thực.
DUR_FMT="$(awk -v d="$DUR" 'BEGIN{printf "%d:%02d", d/60, int(d)%60}')"
{
  echo "Thời điểm : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Chất lượng: $QUALITY ($RES)"
  echo "Thời lượng: $DUR_FMT"
  echo "Git       : $(git rev-parse --short HEAD 2>/dev/null || echo 'không phải git repo')$(git diff --quiet 2>/dev/null || echo ' (có thay đổi chưa commit)')"
  echo "Nhánh     : $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '-')"
  echo
  echo "Scene theo thứ tự:"
  sed -E "s|file '\.\./||; s|'$||" build/concat.txt | sed 's|^|  |'
} > "$SNAP/INFO.txt"

echo
echo "Xong: build/final.mp4, kèm build/final.mkv (softsub)"
echo "Snapshot: $SNAP/"
echo "Thời lượng: $DUR_FMT"
