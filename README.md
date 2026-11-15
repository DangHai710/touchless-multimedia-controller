# Touchless Multimedia Control System

Ứng dụng Python dùng webcam và MediaPipe để điều khiển:

- **Tay trái**: Windows Photo Viewer
- **Tay phải**: YouTube trong Chrome và âm lượng Windows

## Cài đặt trên Windows

Yêu cầu Python **3.11**. MediaPipe hiện không nên chạy bằng Python 3.14
trong project này.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

Nếu `.venv` đã được tạo từ thư mục khác, hãy xóa riêng thư mục `.venv` của
project rồi tạo lại bằng các lệnh trên. Luôn dùng `python -m pip` hoặc đường
dẫn `.venv\Scripts\python.exe -m pip`, không dùng `pip.exe` cũ.

## Điều khiển

### Tay trái - Photo Viewer

- Xòe 5 ngón: bật chế độ điều hướng ảnh
- Chỉ ngón trỏ và vuốt phải: ảnh kế tiếp
- Chỉ ngón trỏ và vuốt trái: ảnh trước
- Nắm tay: đóng cửa sổ đang được focus

### Tay phải - YouTube/âm lượng

- Nắm tay: phát/tạm dừng (`K`)
- Xòe 4 ngón, gập ngón cái: bật/tắt tiếng (`M`)
- Chỉ ngón trỏ và vuốt lên/xuống: tăng/giảm âm lượng Windows
- Chỉ ngón trỏ và vuốt phải/trái: tua tiến/lùi 10 giây (`L`/`J`)

## Lưu ý sử dụng

1. Mở Photo Viewer hoặc Chrome và click vào cửa sổ muốn điều khiển để đặt
   focus trước khi thực hiện cử chỉ.
2. Cửa sổ camera chỉ hiển thị trạng thái; không tự chuyển focus sang Photo
   Viewer hoặc Chrome.
3. Ảnh camera được lật gương để hiển thị tự nhiên. Nhãn `Left`/`Right` của
   MediaPipe được dùng để giữ đúng tay vật lý; không đổi vai trò theo thứ tự
   kết quả nhận diện.
4. Mỗi lệnh có thời gian chờ 10 giây để tránh kích hoạt lặp.
5. Nhấn `Q` hoặc `Esc` trên cửa sổ camera để thoát.

## Cấu trúc

```text
src/
  controller.py  # Gửi phím đến Windows/Chrome
  gesture.py     # Nhận diện ngón tay và vuốt
  hud.py         # Hiển thị trạng thái
  main.py        # Vòng lặp ứng dụng
  tracker.py     # Webcam và phân loại tay trái/phải
```
