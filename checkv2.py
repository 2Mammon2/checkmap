import os
import sys
import time

# Kiểm tra nếu không phải Windows thì thoát
if os.name != "nt":
    print("⚠️ Tool này chỉ chạy trên Windows!")
    input("\nNhấn Enter để thoát...")
    sys.exit()

# Danh sách thư viện cần cài đặt
REQUIRED_LIBRARIES = ["opencv-python", "numpy", "pyautogui", "mss"]

# Hàm kiểm tra & cài đặt thư viện tự động
def install_missing_libraries():
    for lib in REQUIRED_LIBRARIES:
        try:
            __import__(lib.split('-')[0])  # Kiểm tra nếu thư viện đã được import
        except ImportError:
            print(f"📌 Cài đặt thư viện {lib} ...")
            os.system(f'pip install {lib}')  # Cài đặt thư viện

# Gọi hàm để cài đặt thư viện nếu thiếu
install_missing_libraries()

# Import lại sau khi cài đặt
import cv2
import numpy as np
import pyautogui
import mss

# Lấy đường dẫn thư mục thực thi trên Windows
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

# Định nghĩa thư mục chứa ảnh mẫu
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")

# Hàm tìm file ảnh đầu tiên trong thư mục
def get_template_image():
    if not os.path.exists(TEMPLATE_FOLDER):
        print(f"❌ LỖI: Không tìm thấy thư mục {TEMPLATE_FOLDER}")
        input("\nNhấn Enter để thoát...")
        sys.exit()

    # Lấy danh sách file ảnh trong thư mục
    image_files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    if not image_files:
        print(f"❌ LỖI: Không tìm thấy file ảnh trong thư mục {TEMPLATE_FOLDER}")
        input("\nNhấn Enter để thoát...")
        sys.exit()

    return os.path.join(TEMPLATE_FOLDER, image_files[0])

# Lấy đường dẫn file ảnh đầu tiên trong thư mục
TEMPLATE_IMAGE = get_template_image()

# Ngưỡng nhận diện
THRESHOLD = 0.8

# Danh sách tên các vật thể trong spritesheet
OBJECT_NAMES = ["Gold Chest", "Purple Chest", "Mob"]

# Chụp ảnh màn hình
def capture_screen():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # Chụp toàn màn hình
        img = np.array(screenshot)  # Chuyển thành numpy array
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Chuyển đổi màu
        return img

# Tìm rương & quái trên màn hình
def find_objects():
    screen = capture_screen()

    if not os.path.exists(TEMPLATE_IMAGE):
        print(f"❌ LỖI: Không tìm thấy file {TEMPLATE_IMAGE}")
        return {}

    template = cv2.imread(TEMPLATE_IMAGE, cv2.IMREAD_UNCHANGED)

    if template is None:
        print(f"❌ LỖI: Không thể đọc file {TEMPLATE_IMAGE}")
        return {}

    # Dùng OpenCV matchTemplate để tìm đối tượng
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= THRESHOLD)

    # Đếm từng loại rương/quái vật
    object_counts = {name: 0 for name in OBJECT_NAMES}

    for i, pt in enumerate(zip(*locations[::-1])):
        obj_index = i % len(OBJECT_NAMES)  # Xác định loại object theo thứ tự
        obj_name = OBJECT_NAMES[obj_index]
        object_counts[obj_name] += 1

        # Vẽ hình chữ nhật quanh đối tượng
        cv2.rectangle(screen, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 2)

    # Hiển thị kết quả
    cv2.imshow("Dungeon Scanner", screen)
    cv2.waitKey(500)
    cv2.destroyAllWindows()

    return object_counts

# Chạy tool liên tục
while True:
    detected_objects = find_objects()

    if detected_objects:
        print("\n📦 RƯƠNG & QUÁI VẬT:")
        for obj, count in detected_objects.items():
            print(f"- {obj}: {count}")

    time.sleep(5)
