#!/usr/bin/env bash
# Render every section in video order, then stitch into build/final.mp4
#
#   ./build.sh          # 480p15 nháp (mặc định)
#   ./build.sh -qh      # 1080p60 bản cuối
#
# MẶC ĐỊNH CHỈ RENDER SECTION ĐÃ ĐỔI. Một section được coi là cũ khi file .py
# của nó, glance_style.py, hoặc bộ SFX mới hơn các .mp4 đã render — hoặc khi
# thiếu scene. Không đổi gì thì bước render bị bỏ qua hoàn toàn.
#
#   GLANCE_FORCE=1 ./build.sh            # render lại tất, kệ cache
#   GLANCE_NO_RENDER=1 ./build.sh        # không render gì, chỉ ghép + trộn lại
#   GLANCE_SECTIONS="s3 s5" ./build.sh   # ép render đúng 2 section đó
#   GLANCE_NO_MIX=1 ./build.sh           # bỏ bước nhạc nền + SFX
#   GLANCE_BGM=<path> ./build.sh         # đổi nhạc nền
#
# Chỉ đổi nhạc nền hoặc whoosh chuyển cảnh thì KHÔNG cần build:
#   python tools/mix_audio.py            # trộn thẳng lên build/final.mp4, ~30 giây
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
#  3. Ngược lại, có scene audio DÀI hơn video vài trăm ms (manim chốt video theo
#     mốc frame, audio thì không). Với những clip đó, `-shortest` cắt mất đuôi
#     câu cuối: người xem nghe như bị nhảy ngang sang scene sau. Chỗ đó phải kéo
#     dài VIDEO bằng cách giữ frame cuối (tpad) chứ không được cắt audio; chỉ
#     những clip này mới phải mã hoá lại video, còn lại vẫn `-c:v copy`.
normalize() {
  local src="$1" dst="build/norm/$(basename "$1")"
  # Bản chuẩn hoá còn mới hơn clip nguồn thì dùng lại. Trước đây mỗi lần build
  # đều chạy lại đủ 59 lượt ffmpeg kể cả khi không scene nào đổi.
  if [ -f "$dst" ] && [ "$dst" -nt "$src" ]; then
    printf '%s' "$dst"; return
  fi
  if ffprobe -v error -select_streams a -show_entries stream=codec_type \
       -of csv=p=0 "$src" | grep -q audio; then
    local vdur adur gap
    vdur="$(ffprobe -v error -select_streams v -show_entries stream=duration \
             -of default=nw=1:nk=1 "$src")"
    adur="$(ffprobe -v error -select_streams a -show_entries stream=duration \
             -of default=nw=1:nk=1 "$src")"
    gap="$(awk -v a="$adur" -v v="$vdur" 'BEGIN{d=a-v; print (d>0.02)?d:0}')"
    if [ "$gap" != "0" ]; then
      ffmpeg -y -loglevel error -i "$src" \
        -vf "tpad=stop_mode=clone:stop_duration=$(awk -v g="$gap" 'BEGIN{print g+0.1}')" \
        -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
        -c:a aac -b:a 128k -ar 48000 -ac 2 -af apad -shortest "$dst"
    else
      ffmpeg -y -loglevel error -i "$src" \
        -c:v copy -c:a aac -b:a 128k -ar 48000 -ac 2 -af apad -shortest "$dst"
    fi
  else
    ffmpeg -y -loglevel error -i "$src" \
      -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
      -shortest -c:v copy -c:a aac -b:a 128k "$dst"
  fi
  printf '%s' "$dst"
}

# Tên scene theo đúng thứ tự khai báo trong file — dùng cả cho việc dò cache
# lẫn cho việc dựng danh sách ghép.
scene_names() {
  grep -oE '^class ([A-Za-z0-9_]+)\(' "$1" | sed -E 's/^class //; s/\($//'
}

# Những thứ mà MỌI section phụ thuộc vào: sửa chúng là cả video phải render lại.
DEPS_CHUNG=(glance_style.py manim.cfg)
for _w in assets/sfx/*.wav assets/sfx/levels.json; do
  [ -f "$_w" ] && DEPS_CHUNG+=("$_w")
done

# Có cần render lại section này không. File .mp4 của scene nằm sẵn trong
# media/videos/ nên bỏ qua bước render vẫn ghép được video hoàn chỉnh — đây là
# thứ giúp việc sửa nhạc, sửa SFX hay sửa một section không phải trả giá bằng
# 20 phút render toàn bộ.
should_render() {
  local f="$1"
  [ "${GLANCE_NO_RENDER:-0}" = "1" ] && return 1
  [ "${GLANCE_FORCE:-0}" = "1" ] && return 0

  local stem; stem="$(basename "$f" .py)"
  if [ -n "${GLANCE_SECTIONS:-}" ]; then
    local want
    for want in ${GLANCE_SECTIONS}; do
      case "$stem" in *"$want"*) return 0 ;; esac
    done
    return 1
  fi

  # Dò cache: thiếu scene, hoặc có file phụ thuộc mới hơn output -> phải render.
  local dir="media/videos/${stem}/${RES}" scene dep
  [ -d "$dir" ] || return 0
  for scene in $(scene_names "$f"); do
    [ -f "$dir/$scene.mp4" ] || return 0
    for dep in "$f" "${DEPS_CHUNG[@]}"; do
      [ "$dep" -nt "$dir/$scene.mp4" ] && return 0
    done
  done
  return 1
}

for f in "${SECTIONS[@]}"; do
  [ -f "$f" ] || { echo "!! Thiếu file $f — bỏ qua"; continue; }
  if should_render "$f"; then
    echo "==> render $f"
    # --disable_caching: BẮT BUỘC. Cache animation của manim đặt
    # `renderer.skip_animations = True` rồi tự cộng `scene.duration` vào đồng hồ
    # — đường tính thời gian khác hẳn lúc render thật, nên audio bị đặt lệch chỗ
    # và `add_sound` bị bỏ qua. Đã đo: render đè lên cache cho ra track audio chỉ
    # tương quan 0.14 với bản render nguội. Cache ở đây được làm ở mức SECTION
    # (bỏ qua hẳn lệnh manim, xem should_render) — an toàn, vì nó dùng lại chính
    # file .mp4 đã xuất chứ không dựng lại từ mảnh.
    manim "$QUALITY" --disable_caching -a "$f"
  else
    echo "==> bỏ render $f (dùng mp4 có sẵn)"
  fi

  stem="$(basename "$f" .py)"
  # Lấy tên scene theo đúng thứ tự khai báo trong file
  for scene in $(scene_names "$f"); do
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

echo "==> nhạc nền + sound effect"
# Trộn sau khi đã ghép, vì tiếng chuyển cảnh cần biết mốc cắt giữa hai scene —
# thông tin chỉ có ở bước này. Chỉ đụng track audio (-c:v copy) nên mất vài chục
# giây. Bỏ qua bằng GLANCE_NO_MIX=1, đổi nhạc bằng GLANCE_BGM=<đường dẫn>.
if [ "${GLANCE_NO_MIX:-0}" = "1" ]; then
  echo "(bỏ qua: GLANCE_NO_MIX=1)"
else
  python tools/mix_audio.py --bgm "${GLANCE_BGM:-media/audio/dl.mp3}" \
    || echo "(lỗi trộn audio — giữ nguyên bản chưa có nhạc)"
fi

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
