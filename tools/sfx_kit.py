#!/usr/bin/env python3
"""Bộ sound effect tổng hợp cho video GLANCE — một nguồn duy nhất.

    python tools/sfx_kit.py            # ghi toàn bộ .wav ra assets/sfx/
    python tools/sfx_kit.py --list     # xem bảng âm và mức âm lượng

Hai nơi dùng bộ này, và chúng cần nó theo hai cách khác nhau:

  * `tools/mix_audio.py` gọi trực tiếp hàm tổng hợp, rải whoosh ở mốc cắt giữa
    hai scene — thông tin chỉ bước ghép mới biết.
  * Các scene Manim gọi `GlanceScene.sfx("ping")`, cần FILE .wav trên đĩa vì
    `add_sound()` nhận đường dẫn. Accent ngữ nghĩa phải nằm trong scene chứ
    không đặt theo mốc thời gian tuyệt đối: timeline trôi mỗi lần sinh lại một
    câu TTS, một bảng mốc tuyệt đối sẽ sai ngay lần render sau.

Thẩm mỹ: "giao diện khoa học" — tiếng ngắn, sạch, không cộng hưởng dài. Không
tiếng game, không coin, không laser. Đuôi vang không quá 1.2 giây trừ sting
mở/đóng video.

Mọi mức dB dưới đây là TƯƠNG ĐỐI so với độ to trung bình của giọng đọc; đo lúc
chạy chứ không hardcode, xem `mix_audio.py`.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import wave

import numpy as np

SR = 48000

# Mức chuẩn của từng loại, tính bằng dB DƯỚI giọng đọc. Whoosh dày ở mốc đổi
# section là thứ to nhất; tick và blip phải chìm hẳn xuống dưới lời.
LEVELS = {
    "section_whoosh": 6.0,
    "whoosh": 9.0,
    "sting": 9.0,
    "signature": 9.0,
    "ping": 10.0,
    "pulse": 10.0,
    "sweep": 13.0,
    "tick": 15.0,
}


# --------------------------------------------------------------------------
# Khối dựng cơ bản
# --------------------------------------------------------------------------
def _env_swell(n, skew=1.5):
    """Đường bao lên nhanh xuống chậm, đỉnh ở khoảng một phần ba độ dài."""
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    return (np.sin(np.pi * t) ** skew) * np.exp(-1.2 * t)


def _sweep_lowpass(x, fc, poles=3):
    """Thông thấp với tần số cắt chạy theo thời gian — nền của mọi tiếng gió.

    `poles` phải ≥3: một cực chỉ dốc 6 dB/quãng tám nên rò quá nhiều cao tần,
    đo trọng tâm phổ ra 8.4 kHz và nghe thành tiếng "xì" chứ không ra hơi gió.
    """
    a = 1.0 - np.exp(-2.0 * np.pi * fc / SR)
    y = x
    for _ in range(poles):
        out = np.empty_like(y)
        prev = 0.0
        for i in range(y.size):
            prev += a[i] * (y[i] - prev)
            out[i] = prev
        y = out
    return y


def _stereo(mono):
    return np.stack([mono, mono], axis=1)


def _norm(x):
    peak = np.max(np.abs(x))
    return x / peak if peak > 0 else x


def _bell(dur, freq, partials=(1.0, 2.01, 2.99), decay=4.5, detune=0.0007):
    """Chuông mềm: sóng cơ bản cộng hai bồi âm lệch nhẹ cho đỡ khô."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    chans = []
    for ch in range(2):
        acc = np.zeros(n)
        for k, mult in enumerate(partials):
            # Lệch tần rất nhỏ giữa hai kênh tạo bề rộng stereo mà vẫn an toàn
            # khi nghe mono.
            d = 1.0 + detune * (1 if ch else -1) * (k + 1)
            acc += (0.6 ** k) * np.sin(2 * np.pi * freq * mult * d * t)
        chans.append(acc * np.exp(-decay * t / dur))
    return np.stack(chans, axis=1)


def _thump(dur, f_start, f_end):
    """Sine tụt cao độ, tắt nhanh — cú đấm trầm."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f_start * (f_end / f_start) ** (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return _stereo(np.sin(phase) * np.exp(-5.0 * t / dur))


def _noise_whoosh(dur, f_lo, f_hi, seed):
    n = int(dur * SR)
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    fc = f_lo + (f_hi - f_lo) * np.sin(np.pi * t) ** 0.7
    env = _env_swell(n)
    rng = np.random.default_rng(seed)
    chans = []
    for _ in range(2):
        noise = rng.standard_normal(n)
        # Hiệu hai bộ lọc = thông dải, bỏ phần ù đục ở đáy để không lấn nhạc nền.
        band = _sweep_lowpass(noise, fc) - _sweep_lowpass(noise, fc * 0.25)
        chans.append(band * env)
    return np.stack(chans, axis=1)


# --------------------------------------------------------------------------
# Bảy loại tiếng
# --------------------------------------------------------------------------
def section_whoosh():
    """Đổi section: gió dày cộng một cú thump trầm."""
    w = _noise_whoosh(0.70, 240.0, 3200.0, seed=11)
    th = _thump(0.55, 95.0, 44.0) * 0.55
    w[: th.shape[0]] += th
    return w


def whoosh():
    """Chuyển cảnh lớn: một luồng gió ngắn, không thump."""
    return _noise_whoosh(0.42, 340.0, 2600.0, seed=7)


def tick():
    """Click giao diện, rất ngắn — chọn nốt, hiện tín hiệu, chốt quyết định.

    Xung ngắn qua thông thấp: có thân gỗ chứ không phải tiếng "bíp" điện tử.
    """
    n = int(0.055 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    body = rng.standard_normal(n) * np.exp(-90.0 * t)
    body = _sweep_lowpass(body, np.full(n, 2400.0), poles=2)
    body += 0.5 * np.sin(2 * np.pi * 1800 * t) * np.exp(-120.0 * t)
    return _stereo(body)


def ping():
    """Chuông sáng cho kết quả tốt. Cố ý KHÔNG dùng quãng thắng cuộc chói tai."""
    return _bell(0.85, 880.0, partials=(1.0, 2.0, 3.01), decay=6.0)


def pulse():
    """Blip trầm đi xuống cho dự đoán sai, NCS âm, route không hiệu quả."""
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 320.0 * (150.0 / 320.0) ** (t / (n / SR))
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-7.0 * t / (n / SR))
    body += 0.25 * np.sin(2 * phase) * np.exp(-12.0 * t / (n / SR))
    return _stereo(body)


def sweep():
    """Chuỗi blip nhỏ dần — biểu đồ, xác suất, cập nhật véc-tơ."""
    step, k = 0.075, 5
    n = int((step * k + 0.25) * SR)
    out = np.zeros((n, 2))
    for i in range(k):
        b = _bell(0.22, 660.0 * (1.10 ** i), partials=(1.0, 2.0), decay=9.0)
        b *= 0.55 ** i
        s = int(i * step * SR)
        out[s : s + b.shape[0]] += b[: n - s]
    return out


def signature():
    """Dấu hiệu GLANCE: hai nốt tím → cam, dùng khi router đẩy nốt sang LLM."""
    a = _bell(1.10, 523.25, partials=(1.0, 2.0, 3.0), decay=5.0)
    b = _bell(1.30, 783.99, partials=(1.0, 2.0, 2.99), decay=4.2) * 0.8
    off = int(0.17 * SR)
    out = np.zeros((max(a.shape[0], off + b.shape[0]), 2))
    out[: a.shape[0]] += a
    out[off : off + b.shape[0]] += b
    return out


def sting():
    """Mở đầu và kết video: quãng năm đi lên, đuôi dài hơn các tiếng khác."""
    a = _bell(1.70, 528.0)
    b = _bell(1.40, 792.0) * 0.7
    off = int(0.16 * SR)
    a[off : off + b.shape[0]] += b
    return a


KIT = {
    "section_whoosh": section_whoosh,
    "whoosh": whoosh,
    "tick": tick,
    "ping": ping,
    "pulse": pulse,
    "sweep": sweep,
    "signature": signature,
    "sting": sting,
}


# --------------------------------------------------------------------------
def load(name, assets=None):
    """Trả mảng float stereo đã chuẩn hoá đỉnh về 1.0.

    File .wav người dùng bỏ vào `assets` được ưu tiên hơn bản tổng hợp, để thay
    tiếng riêng mà không phải sửa code.
    """
    if assets is not None:
        path = pathlib.Path(assets) / f"{name}.wav"
        if path.is_file():
            with wave.open(str(path), "rb") as w:
                if w.getframerate() != SR or w.getsampwidth() != 2:
                    sys.exit(f"{path}: cần WAV 16-bit {SR}Hz")
                raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                data = raw.reshape(-1, w.getnchannels()).astype(np.float64) / 32768.0
                if data.shape[1] == 1:
                    data = np.repeat(data, 2, axis=1)
            return _norm(data)
    if name not in KIT:
        sys.exit(f"Không có tiếng tên {name!r}. Có: {', '.join(sorted(KIT))}")
    return _norm(KIT[name]())


def write_all(dest):
    dest = pathlib.Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    # Bảng mức ghi kèm ra đĩa: `glance_style.py` đọc file này thay vì chép lại
    # các con số, để chỉnh âm lượng chỉ phải sửa một chỗ.
    import json
    (dest / "levels.json").write_text(json.dumps(LEVELS, indent=2), encoding="utf-8")
    for name, make in KIT.items():
        data = _norm(make())
        path = dest / f"{name}.wav"
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((data * 0.98 * 32767).astype("<i2").tobytes())
        print(f"  {name:<16} {data.shape[0]/SR:5.2f}s  -{LEVELS[name]:.0f} dB dưới giọng")


def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", type=pathlib.Path, default=root / "assets/sfx")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for name in sorted(KIT):
            print(f"  {name:<16} -{LEVELS[name]:.0f} dB dưới giọng đọc")
        return
    print(f"Ghi {len(KIT)} tiếng vào {args.dest}:")
    write_all(args.dest)


if __name__ == "__main__":
    main()
