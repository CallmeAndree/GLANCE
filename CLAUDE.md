# GLANCE — video giải thích paper (Manim)

Trước khi viết, sửa, render hay review bất cứ thứ gì trong repo này, **hãy dùng skill
`glance-video`** (`.claude/skills/glance-video/SKILL.md`). Skill đó chứa quy ước viết
scene, API của `glance_style.py`, lệnh render/build, và cách tự kiểm tra kết quả.

Bốn điều dễ sai nhất:

- Môi trường là **conda env `graphdm`**, không phải venv: `conda activate graphdm`.
- Nội dung mỗi section được đặc tả trong `sections/<folder>/TASK.md` — đọc trước khi code,
  không tự mở rộng phạm vi.
- Số liệu chỉ lấy từ `docs/paper-map.md` hoặc `../GraphDataMining.pdf`. **Không hiện
  citation trên hình** — ghi nguồn bằng comment ngay chỗ dùng số liệu.
- **Chạy `python -m unittest discover -s tests -t .` trước khi mở PR** để kiểm tra
  hạ tầng TTS và các guard kỹ thuật. Render xong mà chưa chạy test là chưa xong.
