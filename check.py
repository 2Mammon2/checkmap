import os
import cv2
import numpy as np
import pyautogui
import mss
import time

# Định nghĩa thư mục chứa ảnh mẫu
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), "templates")  # Thư mục chứa spritesheet

# Hàm tìm file ảnh đầu tiên trong thư mục
def get_template_image():
    if not os.path.exists(TEMPLATE_FOLDER):
        print(f"LỖI: Không tìm thấy thư mục {TEMPLATE_FOLDER}")
        return None

    # Lấy danh sách tất cả file ảnh trong thư mục (PNG, JPG, JPEG)
    image_files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith((".png", ".jpg", ".jpeg"))]

    if not image_files:
        print(f"LỖI: Không tìm thấy file ảnh trong thư mục {TEMPLATE_FOLDER}")
        return None

    # Chọn file đầu tiên trong thư mục
    return os.path.join(TEMPLATE_FOLDER, image_files[0])

# Lấy đường dẫn file ảnh đầu tiên trong thư mục
TEMPLATE_IMAGE = get_template_image()

if TEMPLATE_IMAGE is None:
    exit()  # Thoát chương trình nếu không tìm thấy ảnh mẫu

# Ngưỡng nhận diện (tăng lên nếu bot nhận diện sai)
THRESHOLD = 0.8

# Danh sách tên các vật thể theo thứ tự trong spritesheet
OBJECT_NAMES = ["Gold Chest", "Purple Chest", "Mob"]

# Chụp ảnh màn hình
def capture_screen():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # Chụp toàn màn hình
        img = np.array(screenshot)  # Chuyển thành numpy array
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Chuyển đổi màu
        return img

# Tìm tất cả rương & quái vật trên màn hình
def find_objects():
    screen = capture_screen()

    # Kiểm tra nếu file ảnh bị lỗi
    if not os.path.exists(TEMPLATE_IMAGE):
        print(f"LỖI: Không tìm thấy file {TEMPLATE_IMAGE}")
        return {}

    template = cv2.imread(TEMPLATE_IMAGE, cv2.IMREAD_UNCHANGED)

    if template is None:
        print(f"LỖI: Không thể đọc file {TEMPLATE_IMAGE}")
        return {}

    # Sử dụng matchTemplate để tìm tất cả đối tượng từ ảnh tổng hợp
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= THRESHOLD)

    # Đếm từng loại rương/quái dựa trên vị trí trong spritesheet
    object_counts = {name: 0 for name in OBJECT_NAMES}

    for i, pt in enumerate(zip(*locations[::-1])):
        obj_index = i % len(OBJECT_NAMES)  # Xác định loại object theo thứ tự trong spritesheet
        obj_name = OBJECT_NAMES[obj_index]
        object_counts[obj_name] += 1

        # Vẽ hình chữ nhật quanh đối tượng
        cv2.rectangle(screen, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 2)

    # Hiển thị kết quả
    cv2.imshow("Dungeon Scanner", screen)
    cv2.waitKey(500)  # Hiển thị 0.5s, sau đó tiếp tục quét
    cv2.destroyAllWindows()

    return object_counts

# Chạy bot liên tục
while True:
    detected_objects = find_objects()

    if detected_objects:
        print("\n📦 RƯƠNG & QUÁI VẬT:")
        for obj, count in detected_objects.items():
            print(f"- {obj}: {count}")

    # Đợi 5 giây rồi quét lại
    time.sleep(5)
