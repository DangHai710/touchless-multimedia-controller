"""
main.py — Vòng lặp điều phối chính
Hệ thống điều khiển Xem ảnh & Nghe nhạc/YouTube bằng cử chỉ 2 tay qua webcam.

Cử chỉ chuẩn hóa:
  TAY TRÁI (ẢNH):
    - Xòe 5 ngón                  -> Kích hoạt chế độ PHOTO_NAV
    - Chỉ ngón trỏ vuốt SANG PHẢI -> Chuyển sang ảnh kế tiếp
    - Chỉ ngón trỏ vuốt SANG TRÁI -> Quay về ảnh trước đó
    - Nắm tay (5 ngón gập)        -> Đóng cửa sổ ảnh (Alt+F4)
    - Khoảng nghỉ giữa các thao tác: 10 giây

  TAY PHẢI (YOUTUBE / NHẠC):
    - Nắm tay (5 ngón gập)        -> Play / Tạm dừng video (phím K)
    - Xòe 4 ngón (ngón cái gập)   -> Bật / Tắt tiếng (Mute - phím M)
    - Chỉ ngón trỏ vuốt LÊN       -> Tăng âm lượng Windows
    - Chỉ ngón trỏ vuốt XUỐNG     -> Giảm âm lượng Windows
    - Chỉ ngón trỏ vuốt SANG PHẢI -> Tua tiến 10 giây (phím L)
    - Chỉ ngón trỏ vuốt SANG TRÁI -> Tua lùi 10 giây (phím J)
    - Khoảng nghỉ giữa các thao tác: 10 giây
"""

import sys
import os
import time
import cv2 as cv

# Thêm thư mục src vào đường dẫn Python để import module nội bộ
sys.path.insert(0, os.path.dirname(__file__))

from tracker import Tracker
from gesture import (
    fingers_up,
    five_fingers_open,
    only_index_up,
    fist_closed,
    four_fingers_open_thumb_down,
    get_index_tip,
    get_gesture_name,
    SwipeDetector,
)
from controller import (
    photo_next,
    photo_prev,
    close_active_window,
    volume_up,
    volume_down,
    youtube_seek_forward,
    youtube_seek_back,
    youtube_toggle_play,
    youtube_mute,
)
from hud import HUD


# ─────────────────────────────────────────────────────────────────────────────
# Cấu hình trạng thái & Thời gian nghỉ (Cooldown = 10s)
# ─────────────────────────────────────────────────────────────────────────────

ACTION_COOLDOWN = 10.0  # Khoảng nghỉ 10 giây giữa các thao tác

LEFT_STATE = "IDLE"     # IDLE | PHOTO_NAV
RIGHT_STATE = "IDLE"    # IDLE | YOUTUBE_CTRL

left_last_action_time = 0.0
right_last_action_time = 0.0


def get_wait_time(last_time):
    """Tính số giây còn phải chờ trước khi thực hiện thao tác kế tiếp."""
    passed = time.time() - last_time
    rem = ACTION_COOLDOWN - passed
    return max(0.0, rem)


# ─────────────────────────────────────────────────────────────────────────────
# Xử lý cử chỉ Tay Trái (Điều khiển xem ảnh)
# ─────────────────────────────────────────────────────────────────────────────

def handle_left_hand(hand_lm, swipe_detector, hud, w, h):
    global LEFT_STATE, left_last_action_time

    now = time.time()
    wait_time = get_wait_time(left_last_action_time)
    tip_pos = get_index_tip(hand_lm, w, h)

    # 1. XÒE 5 NGÓN -> Bật chế độ điều hướng ảnh
    if five_fingers_open(hand_lm):
        LEFT_STATE = "PHOTO_NAV"
        swipe_detector.reset()
        return

    # 2. NẮM TAY (5 ngón gập) -> Đóng cửa sổ ảnh
    if fist_closed(hand_lm):
        if wait_time <= 0:
            close_active_window()
            left_last_action_time = now
            LEFT_STATE = "IDLE"
            hud.show_action("DONG ANH (ALT+F4)")
        swipe_detector.reset()
        return

    # 3. CHỈ GIƠ NGÓN TRỎ (các ngón khác gập) -> Theo dõi vuốt chuyển ảnh
    if only_index_up(hand_lm):
        if LEFT_STATE == "PHOTO_NAV":
            swipe = swipe_detector.update(tip_pos)
            if swipe == "SWIPE_RIGHT":
                if wait_time <= 0:
                    photo_next()
                    left_last_action_time = now
                    hud.show_action("ANH KE TIEP >>")
            elif swipe == "SWIPE_LEFT":
                if wait_time <= 0:
                    photo_prev()
                    left_last_action_time = now
                    hud.show_action("<< ANH TRUOC")
        else:
            # Chưa bật PHOTO_NAV thì không vuốt
            swipe_detector.reset()
        return

    # Các cử chỉ khác -> Reset detector để tránh nhận nhầm
    swipe_detector.reset()


# ─────────────────────────────────────────────────────────────────────────────
# Xử lý cử chỉ Tay Phải (Điều khiển YouTube & Âm lượng)
# ─────────────────────────────────────────────────────────────────────────────

def handle_right_hand(hand_lm, swipe_detector, hud, w, h):
    global RIGHT_STATE, right_last_action_time

    now = time.time()
    wait_time = get_wait_time(right_last_action_time)
    tip_pos = get_index_tip(hand_lm, w, h)
    RIGHT_STATE = "YOUTUBE_CTRL"

    # 1. NẮM TAY (5 ngón gập) -> Play / Pause video YouTube
    if fist_closed(hand_lm):
        if wait_time <= 0:
            youtube_toggle_play()
            right_last_action_time = now
            hud.show_action("PLAY / PAUSE")
        swipe_detector.reset()
        return

    # 2. XÒE 4 NGÓN (ngón cái gập) -> Mute / Unmute YouTube
    if four_fingers_open_thumb_down(hand_lm):
        if wait_time <= 0:
            youtube_mute()
            right_last_action_time = now
            hud.show_action("BAT / TAT TIENG (MUTE)")
        swipe_detector.reset()
        return

    # 3. CHỈ GIƠ NGÓN TRỎ (các ngón khác gập) -> Vuốt âm lượng hoặc tua video
    if only_index_up(hand_lm):
        swipe = swipe_detector.update(tip_pos)
        if swipe == "SWIPE_UP":
            if wait_time <= 0:
                volume_up(steps=4)
                right_last_action_time = now
                hud.show_action("^ TANG AM LUONG")
        elif swipe == "SWIPE_DOWN":
            if wait_time <= 0:
                volume_down(steps=4)
                right_last_action_time = now
                hud.show_action("v GIAM AM LUONG")
        elif swipe == "SWIPE_RIGHT":
            if wait_time <= 0:
                youtube_seek_forward()
                right_last_action_time = now
                hud.show_action("TUA TIEN +10s >>")
        elif swipe == "SWIPE_LEFT":
            if wait_time <= 0:
                youtube_seek_back()
                right_last_action_time = now
                hud.show_action("<< TUA LUI -10s")
        return

    # Các cử chỉ khác -> Reset detector
    swipe_detector.reset()


# ─────────────────────────────────────────────────────────────────────────────
# VÒNG LẶP CHÍNH
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global LEFT_STATE, RIGHT_STATE

    tracker = Tracker(num_hands=2, cam_index=0)

    # Thử kết nối camera
    ok, test_frame = tracker.video_capture.read()
    if not ok or test_frame is None:
        print("[LOI] Khong the ket noi webcam. Vui long kiem tra camera.")
        return

    h, w = test_frame.shape[:2]

    # Khởi tạo bộ phát hiện vuốt ngón trỏ riêng cho 2 tay
    swipe_left = SwipeDetector(threshold=55, history_len=7, cooldown=0.7)
    swipe_right = SwipeDetector(threshold=55, history_len=7, cooldown=0.7)

    # Khởi tạo giao diện HUD
    hud = HUD()

    win_name = "Dieu khien cu chi: Anh & Nhac - Nhan Q de thoat"
    cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    cv.resizeWindow(win_name, min(w, 960), min(h, 540))

    print("=" * 60)
    print("  HE THONG DIEU KHIEN CU CHI 2 TAY (DA CAP NHAT)")
    print("=" * 60)
    print("  TAY TRAI (ANH):")
    print("    - Xoe 5 ngon           -> Bat che do xem anh (PHOTO_NAV)")
    print("    - Chi ngon tro sang phai -> Anh ke tiep")
    print("    - Chi ngon tro sang trai -> Anh truoc")
    print("    - Nam tay (5 ngon)      -> Dong cua so anh (Alt+F4)")
    print("    * Khoang nghi: 10s giua cac thao tac")
    print()
    print("  TAY PHAI (YOUTUBE / NHAC):")
    print("    - Nam tay (5 ngon)      -> Play / Pause")
    print("    - Xoe 4 ngon (gap cai)  -> Mute / Unmute")
    print("    - Chi ngon tro len      -> Tang am luong Windows")
    print("    - Chi ngon tro xuong    -> Giam am luong Windows")
    print("    - Chi ngon tro sang phai -> Tua +10 giay")
    print("    - Chi ngon tro sang trai -> Tua -10 giay")
    print("    * Khoang nghi: 10s giua cac thao tac")
    print("=" * 60)
    print("  Chu y: Click vao Photo hoac Chrome de ung dung duoc focus truoc.")
    print("  Nhan Q hoac ESC tren cua so camera de thoat.")
    print()

    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            print("[CANH BAO] Mat ket noi webcam.")
            break

        # Phân loại chính xác Tay Trái và Tay Phải
        left_hand, right_hand = tracker.split_hands(results)

        # Vẽ khung xương nhận diện
        if left_hand:
            tracker.draw_landmarks(frame, left_hand)
        if right_hand:
            tracker.draw_landmarks(frame, right_hand)

        # Tính toán cử chỉ và thời gian nghỉ
        left_gesture = get_gesture_name(left_hand)
        right_gesture = get_gesture_name(right_hand)
        left_wait = get_wait_time(left_last_action_time)
        right_wait = get_wait_time(right_last_action_time)

        # Xử lý tay trái
        if left_hand:
            handle_left_hand(left_hand, swipe_left, hud, w, h)
        else:
            swipe_left.reset()

        # Xử lý tay phải
        if right_hand:
            handle_right_hand(right_hand, swipe_right, hud, w, h)
        else:
            swipe_right.reset()

        # Vẽ HUD thông tin chi tiết
        hud.draw(
            frame,
            LEFT_STATE, RIGHT_STATE,
            left_gesture, right_gesture,
            left_wait, right_wait,
            left_hand, right_hand,
            w, h,
        )
        hud.draw_title_bar(frame, w)

        # Hiển thị ra cửa sổ
        cv.imshow(win_name, frame)

        # Nhấn Q hoặc ESC để thoát
        key = cv.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break

    tracker.release()
    cv.destroyAllWindows()
    print("Da thoat chuong trinh.")


if __name__ == "__main__":
    main()
