"""
tracker.py — Module quản lý webcam và trích xuất bàn tay
Sử dụng OpenCV và MediaPipe Hands.
Đã xử lý chính xác việc phân biệt Tay Trái / Tay Phải trên khung hình soi gương (mirrored frame).
"""

import cv2 as cv
import mediapipe as mp


class Tracker:
    """
    Chịu trách nhiệm:
    1. Kết nối và đọc luồng webcam
    2. Chạy model AI MediaPipe Hands để trích xuất 21 điểm mốc (landmarks)
    3. Phân biệt chính xác Tay Trái / Tay Phải của người dùng
    """

    def __init__(self, num_hands=2, cam_index=0):
        # Kết nối webcam (cam_index=0 là camera mặc định)
        self.video_capture = cv.VideoCapture(cam_index)

        # Khởi tạo model AI MediaPipe Hands
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=num_hands,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        self.draw_utils = mp.solutions.drawing_utils
        self.hand_connections = mp_hands.HAND_CONNECTIONS

    def get_frame(self):
        """
        Đọc 1 frame từ webcam, lật gương và chạy MediaPipe.
        Trả về:
        - frame: ảnh BGR đã lật gương (chuẩn soi gương)
        - results: kết quả nhận diện từ MediaPipe
        """
        ok, frame = self.video_capture.read()
        if not ok:
            return None, None

        # Lật ảnh theo trục Y để tạo hiệu ứng soi gương cho người dùng
        frame = cv.flip(frame, 1)

        # Chuyển đổi BGR sang RGB cho MediaPipe
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        return frame, results

    def draw_landmarks(self, frame, hand_landmarks):
        """Vẽ khung xương bàn tay lên frame."""
        self.draw_utils.draw_landmarks(
            frame, hand_landmarks, self.hand_connections
        )

    def split_hands(self, results):
        """
        Phân loại chính xác Tay Trái và Tay Phải của người dùng.

        LƯU Ý QUAN TRỌNG VỀ LẬT GƯƠNG (MIRROR EFFECT):
        Vì ảnh đầu vào đã được lật ngang (cv.flip), góc nhìn giải phẫu học của
        MediaPipe sẽ bị đảo ngược:
          - MediaPipe 'Right' -> Thực tế là TAY TRÁI của người dùng
          - MediaPipe 'Left'  -> Thực tế là TAY PHẢI của người dùng

        Đồng thời, kết hợp vị trí tọa độ X trên màn hình soi gương:
          - Tay bên trái màn hình (x nhỏ hơn) = TAY TRÁI của người dùng
          - Tay bên phải màn hình (x lớn hơn) = TAY PHẢI của người dùng

        Trả về: (left_hand_landmarks, right_hand_landmarks)
        """
        left_hand = None
        right_hand = None

        if not results.multi_hand_landmarks:
            return None, None

        detected = []
        for idx, hand_lm in enumerate(results.multi_hand_landmarks):
            mp_label = results.multi_handedness[idx].classification[0].label
            score = results.multi_handedness[idx].classification[0].score
            wrist_x = hand_lm.landmark[0].x  # Landmark 0 = Cổ tay (Wrist)
            detected.append({
                "landmarks": hand_lm,
                "mp_label": mp_label,
                "score": score,
                "wrist_x": wrist_x,
            })

        if len(detected) == 1:
            h = detected[0]
            # Đảo nhãn MediaPipe do lật gương: 'Right' -> Trái thực tế, 'Left' -> Phải thực tế
            is_physical_left = (h["mp_label"] == "Right")

            # Kiểm tra phụ theo vị trí nửa màn hình nếu ở vùng biên rõ ràng
            if h["wrist_x"] < 0.35:
                is_physical_left = True
            elif h["wrist_x"] > 0.65:
                is_physical_left = False

            if is_physical_left:
                left_hand = h["landmarks"]
            else:
                right_hand = h["landmarks"]

        elif len(detected) >= 2:
            # Khi có 2 bàn tay trong khung hình soi gương:
            # Bàn tay có tọa độ X nhỏ hơn chắc chắn là TAY TRÁI (nằm bên trái người dùng)
            # Bàn tay có tọa độ X lớn hơn chắc chắn là TAY PHẢI (nằm bên phải người dùng)
            detected.sort(key=lambda item: item["wrist_x"])
            left_hand = detected[0]["landmarks"]
            right_hand = detected[1]["landmarks"]

        return left_hand, right_hand

    def release(self):
        """Giải phóng tài nguyên camera."""
        self.video_capture.release()
