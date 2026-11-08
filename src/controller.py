"""
controller.py — Module gửi lệnh điều khiển đến Windows và Chrome
Dùng pyautogui để gửi phím ảo:
  - Tay Trái: Điều khiển Windows Photo Viewer (xem ảnh)
  - Tay Phải: Điều khiển âm lượng Windows + YouTube trên Chrome
"""

import pyautogui
import time

# Tắt tính năng fail-safe của pyautogui (di chuột góc màn hình sẽ không dừng)
# Đặt False để tránh chương trình bị dừng đột ngột khi tay di chuyển mạnh
pyautogui.FAILSAFE = False

# Độ trễ giữa các phím tắt kép (ví dụ: Alt+F4)
pyautogui.PAUSE = 0.05


# ─────────────────────────────────────────────────────────────────────────────
# CÁC LỆNH ĐIỀU KHIỂN ẢNH (Tay Trái)
# ─────────────────────────────────────────────────────────────────────────────

def photo_next():
    """
    Chuyển sang ảnh KẾ TIẾP trong Windows Photo Viewer.
    Phím tắt: → (mũi tên sang phải)
    """
    pyautogui.press("right")


def photo_prev():
    """
    Quay về ảnh TRƯỚC ĐÓ trong Windows Photo Viewer.
    Phím tắt: ← (mũi tên sang trái)
    """
    pyautogui.press("left")


def close_active_window():
    """
    Đóng cửa sổ đang được focus (Photo Viewer hoặc bất kỳ cửa sổ nào).
    Phím tắt: Alt + F4
    """
    pyautogui.hotkey("alt", "f4")


# ─────────────────────────────────────────────────────────────────────────────
# CÁC LỆNH ĐIỀU KHIỂN NHẠC / YOUTUBE (Tay Phải)
# ─────────────────────────────────────────────────────────────────────────────

def volume_up(steps=3):
    """
    Tăng âm lượng hệ thống Windows.
    Mỗi lần nhấn volumeup = tăng khoảng 2%.
    steps=3 → tăng khoảng 6% mỗi cử chỉ vuốt lên.
    """
    for _ in range(steps):
        pyautogui.press("volumeup")


def volume_down(steps=3):
    """
    Giảm âm lượng hệ thống Windows.
    steps=3 → giảm khoảng 6% mỗi cử chỉ vuốt xuống.
    """
    for _ in range(steps):
        pyautogui.press("volumedown")


def youtube_seek_forward():
    """
    Tua YouTube tiến thêm 10 giây.
    Phím tắt YouTube: L
    (Lưu ý: Chrome/YouTube phải đang ở foreground hoặc tab đang active)
    """
    pyautogui.press("l")


def youtube_seek_back():
    """
    Tua YouTube lùi lại 10 giây.
    Phím tắt YouTube: J
    """
    pyautogui.press("j")


def youtube_toggle_play():
    """
    Tạm dừng hoặc tiếp tục phát YouTube.
    Phím tắt YouTube: Space hoặc K
    """
    pyautogui.press("k")


def youtube_mute():
    """
    Bật/Tắt tiếng trên YouTube.
    Phím tắt YouTube: M
    """
    pyautogui.press("m")


def youtube_fullscreen():
    """
    Bật/Tắt chế độ toàn màn hình trên YouTube.
    Phím tắt YouTube: F
    """
    pyautogui.press("f")
