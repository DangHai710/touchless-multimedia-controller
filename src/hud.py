"""
hud.py — Module vẽ giao diện overlay lên frame camera
Hiển thị:
  - Góc trên trái: Trạng thái tay trái + Cử chỉ nhận diện + Đếm ngược nghỉ (10s) + Hướng dẫn ảnh
  - Góc trên phải: Trạng thái tay phải + Cử chỉ nhận diện + Đếm ngược nghỉ (10s) + Hướng dẫn nhạc
  - Giữa màn hình: Thông báo hành động lớn nổi bật khi vừa kích hoạt lệnh
  - Tâm ngắm ngón trỏ khi đang ở tư thế chỉ ngón trỏ
"""

import cv2 as cv
import time


# ─────────────────────────────────────────────────────────────────────────────
# Bảng màu (BGR format vì OpenCV dùng BGR)
# ─────────────────────────────────────────────────────────────────────────────
COLOR_WHITE   = (255, 255, 255)
COLOR_BLACK   = (0,   0,   0  )
COLOR_GREEN   = (0,   220, 100)   # Tay trái (ảnh) / Sẵn sàng
COLOR_ORANGE  = (0,   165, 255)   # Tay phải (nhạc)
COLOR_YELLOW  = (0,   220, 255)   # Animation / Cảnh báo
COLOR_RED     = (60,  60,  255)   # Đang chờ (cooldown)
COLOR_GRAY    = (140, 140, 140)
COLOR_PANEL   = (20,  20,  20 )   # Nền panel (gần đen)

FONT = cv.FONT_HERSHEY_SIMPLEX


# ─────────────────────────────────────────────────────────────────────────────

class HUD:
    """
    Lớp quản lý tất cả nội dung overlay lên frame camera.
    """

    def __init__(self):
        self._action_text = ""         # Chữ hiển thị khi có hành động
        self._action_show_until = 0.0  # Thời điểm hết hiển thị
        self._action_duration = 1.2    # Thời gian hiển thị (giây)

    def show_action(self, action_text):
        """
        Kích hoạt hiển thị banner thông báo hành động ở trung tâm màn hình.
        """
        self._action_text = action_text
        self._action_show_until = time.time() + self._action_duration

    def draw(self, frame,
             left_state, right_state,
             left_gesture, right_gesture,
             left_wait, right_wait,
             left_hand_lm, right_hand_lm,
             w, h):
        """
        Vẽ toàn bộ overlay lên frame.
        """
        self._draw_left_panel(frame, left_state, left_gesture, left_wait, left_hand_lm, w, h)
        self._draw_right_panel(frame, right_state, right_gesture, right_wait, right_hand_lm, w, h)
        self._draw_action_banner(frame, w, h)
        self._draw_pointer(frame, left_hand_lm, right_hand_lm, w, h)

    def _draw_left_panel(self, frame, state, gesture, wait_time, hand_lm, w, h):
        """Panel góc trên trái: thông tin điều khiển ảnh (tay trái)."""
        overlay = frame.copy()
        cv.rectangle(overlay, (10, 10), (310, 225), COLOR_PANEL, -1)
        cv.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

        # Tiêu đề
        status_color = COLOR_GREEN if hand_lm else COLOR_GRAY
        cv.putText(frame, "TAY TRAI (ANH)", (20, 32),
                   FONT, 0.55, status_color, 2)

        # Trạng thái kết nối
        dot_color = COLOR_GREEN if hand_lm else (60, 60, 60)
        cv.circle(frame, (295, 25), 7, dot_color, -1)

        # Mode
        cv.putText(frame, f"Che do: {state}", (20, 55),
                   FONT, 0.45, COLOR_WHITE, 1)

        # Cử chỉ nhận diện
        cv.putText(frame, f"Cu chi: {gesture}", (20, 77),
                   FONT, 0.42, COLOR_YELLOW, 1)

        # Đếm ngược thời gian nghỉ (Cooldown 10s)
        if wait_time > 0:
            wait_str = f"CHO NGHI: {wait_time:.1f}s"
            cv.putText(frame, wait_str, (20, 100),
                       FONT, 0.45, COLOR_RED, 2)
        else:
            cv.putText(frame, "TRANG THAI: SAN SANG", (20, 100),
                       FONT, 0.42, COLOR_GREEN, 1)

        # Đường kẻ ngang phân cách
        cv.line(frame, (20, 110), (300, 110), COLOR_GRAY, 1)

        # Hướng dẫn thao tác
        tips_left = [
            "Xoe 5 ngon     : Bat xem anh",
            "Tro vuot PHAI  : Anh ke tiep",
            "Tro vuot TRAI  : Anh truoc",
            "Nam tay 5 ngon : Dong anh (Alt+F4)",
            "Nghi 10s giua cac thao tac",
        ]
        for i, tip in enumerate(tips_left):
            cv.putText(frame, tip, (20, 130 + i * 19),
                       FONT, 0.36, COLOR_GRAY, 1)

    def _draw_right_panel(self, frame, state, gesture, wait_time, hand_lm, w, h):
        """Panel góc trên phải: thông tin điều khiển nhạc/YouTube (tay phải)."""
        px = w - 320
        overlay = frame.copy()
        cv.rectangle(overlay, (px, 10), (w - 10, 245), COLOR_PANEL, -1)
        cv.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

        # Tiêu đề
        status_color = COLOR_ORANGE if hand_lm else COLOR_GRAY
        cv.putText(frame, "TAY PHAI (YOUTUBE)", (px + 10, 32),
                   FONT, 0.55, status_color, 2)

        # Trạng thái kết nối
        dot_color = COLOR_ORANGE if hand_lm else (60, 60, 60)
        cv.circle(frame, (w - 25, 25), 7, dot_color, -1)

        # Mode
        cv.putText(frame, f"Che do: {state}", (px + 10, 55),
                   FONT, 0.45, COLOR_WHITE, 1)

        # Cử chỉ nhận diện
        cv.putText(frame, f"Cu chi: {gesture}", (px + 10, 77),
                   FONT, 0.42, COLOR_YELLOW, 1)

        # Đếm ngược thời gian nghỉ (Cooldown 10s)
        if wait_time > 0:
            wait_str = f"CHO NGHI: {wait_time:.1f}s"
            cv.putText(frame, wait_str, (px + 10, 100),
                       FONT, 0.45, COLOR_RED, 2)
        else:
            cv.putText(frame, "TRANG THAI: SAN SANG", (px + 10, 100),
                       FONT, 0.42, COLOR_GREEN, 1)

        # Đường kẻ ngang phân cách
        cv.line(frame, (px + 10, 110), (w - 20, 110), COLOR_GRAY, 1)

        # Hướng dẫn thao tác
        tips_right = [
            "Nam tay 5 ngon : Play / Pause",
            "Xoe 4 ngon     : Mute / Unmute",
            "Tro vuot LEN   : Tang am luong",
            "Tro vuot XUONG : Giam am luong",
            "Tro vuot PHAI  : Tua +10 giay",
            "Tro vuot TRAI  : Tua -10 giay",
            "Nghi 10s giua cac thao tac",
        ]
        for i, tip in enumerate(tips_right):
            cv.putText(frame, tip, (px + 10, 130 + i * 19),
                       FONT, 0.36, COLOR_GRAY, 1)

    def _draw_action_banner(self, frame, w, h):
        """Hiển thị banner thông báo hành động ở giữa màn hình."""
        if not self._action_text:
            return
        now = time.time()
        if now > self._action_show_until:
            self._action_text = ""
            return

        ratio = (self._action_show_until - now) / self._action_duration
        alpha = max(0.2, min(1.0, ratio))

        overlay = frame.copy()
        txt_size, _ = cv.getTextSize(self._action_text, FONT, 1.1, 2)
        cx = (w - txt_size[0]) // 2
        cy = h // 2
        pad_x = 25
        pad_y = 18

        cv.rectangle(overlay,
                     (cx - pad_x, cy - txt_size[1] - pad_y),
                     (cx + txt_size[0] + pad_x, cy + pad_y),
                     (10, 10, 10), -1)
        cv.rectangle(overlay,
                     (cx - pad_x, cy - txt_size[1] - pad_y),
                     (cx + txt_size[0] + pad_x, cy + pad_y),
                     COLOR_YELLOW, 2)
        cv.addWeighted(overlay, 0.85 * alpha, frame, 1 - 0.85 * alpha, 0, frame)

        color = tuple(int(c * alpha) for c in COLOR_YELLOW)
        cv.putText(frame, self._action_text, (cx, cy),
                   FONT, 1.1, color, 2)

    def _draw_pointer(self, frame, left_hand_lm, right_hand_lm, w, h):
        """Vẽ tâm ngắm tại đầu ngón trỏ."""
        for hand_lm, color in [
            (left_hand_lm,  COLOR_GREEN),
            (right_hand_lm, COLOR_ORANGE),
        ]:
            if hand_lm is None:
                continue
            tip = hand_lm.landmark[8]
            px = int(tip.x * w)
            py = int(tip.y * h)
            cv.circle(frame, (px, py), 12, color, 2)
            cv.drawMarker(frame, (px, py), color, cv.MARKER_CROSS, 18, 2)

    def draw_title_bar(self, frame, w):
        """Vẽ thanh tiêu đề nhỏ ở dưới cùng màn hình."""
        overlay = frame.copy()
        h = frame.shape[0]
        cv.rectangle(overlay, (0, h - 32), (w, h), COLOR_PANEL, -1)
        cv.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv.putText(frame,
                   "Q / ESC: Thoat | Click vao Photo hoac Chrome truoc de focus ung dung",
                   (15, h - 10), FONT, 0.42, COLOR_WHITE, 1)
