"""
gesture.py — Module nhận diện cử chỉ tay nâng cao
Hỗ trợ các cử chỉ:
  1. five_fingers_open()          : Xòe 5 ngón (bao gồm ngón cái)
  2. only_index_up()              : Chỉ giơ ngón trỏ, các ngón khác gập lại
  3. fist_closed()                : Nắm tay (5 ngón đều gập)
  4. four_fingers_open_thumb_down : Xòe 4 ngón, ngón cái gập
  5. SwipeDetector                : Phát hiện cử chỉ vuốt 4 hướng bằng ngón trỏ
"""

from collections import deque
import time


# ─────────────────────────────────────────────────────────────────────────────
# Nhận diện trạng thái từng ngón tay
# Landmark MediaPipe:
#   0: Cổ tay (Wrist)
#   4: Đầu ngón cái (Thumb tip)
#   8: Đầu ngón trỏ (Index tip)    |  6: Khớp PIP ngón trỏ
#  12: Đầu ngón giữa (Middle tip)   | 10: Khớp PIP ngón giữa
#  16: Đầu ngón áp út (Ring tip)    | 14: Khớp PIP ngón áp út
#  20: Đầu ngón út (Pinky tip)      | 18: Khớp PIP ngón út
#   9: Khớp MCP ngón giữa (Gốc ngón giữa)
#  17: Khớp MCP ngón út (Gốc ngón út)
# ─────────────────────────────────────────────────────────────────────────────

def is_thumb_open(hand_landmarks):
    """
    Kiểm tra ngón cái đang xòe hay gập vào lòng bàn tay.
    Sử dụng khoảng cách chuẩn hóa theo tỉ lệ bàn tay (scale-invariant):
    - Khi ngón cái xòe: Khoảng cách từ đầu ngón cái (4) đến gốc ngón út (17) lớn.
    - Khi ngón cái gập: Ngón cái khép vào lòng bàn tay, khoảng cách thu nhỏ.
    """
    lm = hand_landmarks.landmark
    # Chiều dài chuẩn của bàn tay: từ cổ tay (0) đến khớp gốc ngón giữa (9)
    scale = ((lm[0].x - lm[9].x) ** 2 + (lm[0].y - lm[9].y) ** 2) ** 0.5
    if scale < 1e-4:
        return False

    # Khoảng cách từ đầu ngón cái (4) đến gốc ngón út (17)
    d_thumb_pinky = ((lm[4].x - lm[17].x) ** 2 + (lm[4].y - lm[17].y) ** 2) ** 0.5
    ratio = d_thumb_pinky / scale
    return ratio > 0.65


def fingers_up(hand_landmarks):
    """
    Kiểm tra trạng thái 4 ngón: trỏ, giữa, áp út, út.
    Trả về: list 4 giá trị bool [trỏ, giữa, áp út, út]
    Điều kiện giơ: Tọa độ y của đầu ngón (tip) cao hơn khớp đốt giữa (pip = tip - 2).
    """
    tips = [8, 12, 16, 20]
    result = []
    for tip in tips:
        is_up = hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y
        result.append(is_up)
    return result


def five_fingers_open(hand_landmarks):
    """
    Cử chỉ: XÒE CẢ 5 NGÓN TAY.
    - Cả 4 ngón (trỏ, giữa, áp út, út) đều giơ lên.
    - Ngón cái đang xòe mở.
    Dùng để: Bật chế độ xem ảnh PHOTO_NAV (tay trái).
    """
    four = fingers_up(hand_landmarks)
    thumb = is_thumb_open(hand_landmarks)
    return all(four) and thumb


def only_index_up(hand_landmarks):
    """
    Cử chỉ: CHỈ GIƠ DUY NHẤT NGÓN TRỎ, CÁC NGÓN KHÁC GẬP LẠI.
    - Ngón trỏ giơ (True)
    - Ngón giữa, áp út, út đều gập (False)
    - Ngón cái gập hoặc áp sát lòng bàn tay
    Dùng để: Chuẩn bị thực hiện thao tác vuốt (Swipe) chuyển ảnh/tăng giảm âm/tua nhạc.
    """
    four = fingers_up(hand_landmarks)
    index_is_up = four[0]
    others_down = not four[1] and not four[2] and not four[3]
    return index_is_up and others_down


def fist_closed(hand_landmarks):
    """
    Cử chỉ: NẮM TAY (NẮM ĐẤM - CẢ 5 NGÓN GẬP).
    - Cả 4 ngón chính (trỏ, giữa, áp út, út) đều gập xuống.
    - Ngón cái gập khép vào lòng bàn tay.
    Dùng để:
      - Tay trái: Đóng cửa sổ ảnh (Alt+F4).
      - Tay phải: Play / Tạm dừng phát YouTube.
    """
    four = fingers_up(hand_landmarks)
    thumb = is_thumb_open(hand_landmarks)
    return (not any(four)) and (not thumb)


def four_fingers_open_thumb_down(hand_landmarks):
    """
    Cử chỉ: XÒE 4 NGÓN, NGÓN CÁI GẬP.
    - 4 ngón (trỏ, giữa, áp út, út) đều giơ lên.
    - Ngón cái gập vào lòng bàn tay.
    Dùng để: Tắt / Bật tiếng YouTube (Mute / Unmute).
    """
    four = fingers_up(hand_landmarks)
    thumb = is_thumb_open(hand_landmarks)
    return all(four) and (not thumb)


def get_index_tip(hand_landmarks, frame_w, frame_h):
    """
    Lấy tọa độ pixel của đầu ngón trỏ (Landmark 8).
    Trả về: (x, y) là tọa độ pixel nguyên.
    """
    tip = hand_landmarks.landmark[8]
    x = int(tip.x * frame_w)
    y = int(tip.y * frame_h)
    return x, y


def get_gesture_name(hand_landmarks):
    """
    Trả về chuỗi tên cử chỉ hiện tại để hiển thị trực quan lên HUD.
    """
    if hand_landmarks is None:
        return "KHONG CO TAY"
    if fist_closed(hand_landmarks):
        return "NAM TAY (5 NGON GAP)"
    if five_fingers_open(hand_landmarks):
        return "XOE 5 NGON"
    if four_fingers_open_thumb_down(hand_landmarks):
        return "XOE 4 NGON (GAP CAI)"
    if only_index_up(hand_landmarks):
        return "CHI NGON TRO (VUOT)"
    return "DANG DOI CU CHI"


# ─────────────────────────────────────────────────────────────────────────────
# Bộ phát hiện cử chỉ vuốt (SwipeDetector)
# ─────────────────────────────────────────────────────────────────────────────

class SwipeDetector:
    """
    Phát hiện cử chỉ vuốt ngón trỏ theo 4 hướng:
      SWIPE_LEFT, SWIPE_RIGHT, SWIPE_UP, SWIPE_DOWN.
    Chỉ kích hoạt khi người dùng đang ở tư thế CHỈ GIƠ NGÓN TRỎ.
    """

    def __init__(self, threshold=55, history_len=7, cooldown=0.7):
        self.threshold = threshold
        self.cooldown = cooldown
        self.history = deque(maxlen=history_len)
        self._last_swipe_time = 0.0

    def update(self, point):
        """
        Cập nhật tọa độ đầu ngón trỏ và phân tích chuyển động.
        point: tuple (x, y) hoặc None
        """
        if point is None:
            self.history.clear()
            return None

        self.history.append(point)

        now = time.time()
        if len(self.history) < self.history.maxlen:
            return None
        if now - self._last_swipe_time < self.cooldown:
            return None

        x_start, y_start = self.history[0]
        x_end, y_end = self.history[-1]
        dx = x_end - x_start
        dy = y_end - y_start

        swipe = None

        # Vuốt ngang: |dx| vượt ngưỡng và chiếm ưu thế rõ rệt
        if abs(dx) > self.threshold and abs(dx) > 1.3 * abs(dy):
            swipe = "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"

        # Vuốt dọc: |dy| vượt ngưỡng và chiếm ưu thế rõ rệt (trục y hướng xuống: dy < 0 là lên)
        elif abs(dy) > self.threshold and abs(dy) > 1.3 * abs(dx):
            swipe = "SWIPE_UP" if dy < 0 else "SWIPE_DOWN"

        if swipe:
            self.history.clear()
            self._last_swipe_time = now

        return swipe

    def reset(self):
        """Xóa lịch sử khi người dùng đổi tư thế ngón tay."""
        self.history.clear()
