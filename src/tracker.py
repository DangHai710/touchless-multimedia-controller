"""
tracker.py — Module quản lý webcam và trích xuất bàn tay.
Sử dụng OpenCV và MediaPipe Hands.
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
        Phân loại tay trái/phải theo nhãn handedness của MediaPipe.

        ``get_frame`` đã lật ảnh thành dạng soi gương trước khi gọi
        ``hands.process``. MediaPipe được thiết kế để nhận ảnh soi gương, vì
        vậy nhãn ``Left``/``Right`` lúc này là tay trái/phải thực tế của
        người dùng và không được đảo lại. Tọa độ X chỉ dùng khi kết quả thiếu
        nhãn hoặc MediaPipe trả về hai nhãn trùng nhau.

        Trả về: (left_hand_landmarks, right_hand_landmarks)
        """
        if results is None or not results.multi_hand_landmarks:
            return None, None

        detected = []
        for idx, hand_lm in enumerate(results.multi_hand_landmarks):
            mp_label = None
            score = 0.0
            if (
                results.multi_handedness
                and idx < len(results.multi_handedness)
                and results.multi_handedness[idx].classification
            ):
                classification = results.multi_handedness[idx].classification[0]
                mp_label = classification.label
                score = classification.score
            wrist_x = hand_lm.landmark[0].x  # Landmark 0 = Cổ tay (Wrist)
            detected.append({
                "landmarks": hand_lm,
                "mp_label": mp_label,
                "score": score,
                "wrist_x": wrist_x,
            })

        left_candidates = [
            item for item in detected if item["mp_label"] == "Left"
        ]
        right_candidates = [
            item for item in detected if item["mp_label"] == "Right"
        ]

        # Dùng nhãn có độ tin cậy cao nhất khi MediaPipe nhận diện đủ hai bên.
        left = max(left_candidates, key=lambda item: item["score"], default=None)
        right = max(right_candidates, key=lambda item: item["score"], default=None)
        assigned = {id(left), id(right)} - {id(None)}
        unassigned = [item for item in detected if id(item) not in assigned]

        if len(detected) == 1 and unassigned:
            # Khi chỉ có một tay và nhãn không dùng được, vị trí giữa khung
            # là ranh giới an toàn nhất để chọn vai trò tạm thời. Vì ảnh đã
            # soi gương, tay trái thực tế xuất hiện ở phía phải khung hình.
            item = unassigned[0]
            if item["wrist_x"] > 0.5:
                left = item
            else:
                right = item
            unassigned.clear()

        # Nếu nhãn bị thiếu/trùng, xếp phần còn lại theo vị trí trên ảnh soi gương.
        # Trên ảnh soi gương, tay trái thực tế nằm phía phải khung hình.
        unassigned.sort(key=lambda item: item["wrist_x"], reverse=True)
        if left is None and unassigned:
            left = unassigned.pop(0)
        if right is None and unassigned:
            right = unassigned.pop(0)

        return (
            left["landmarks"] if left is not None else None,
            right["landmarks"] if right is not None else None,
        )

    def release(self):
        """Giải phóng tài nguyên camera."""
        self.video_capture.release()
