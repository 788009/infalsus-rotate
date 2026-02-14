import socket
import pydirectinput
from pynput import keyboard

# 配置
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
SCREEN_WIDTH = 2880  # 你的屏幕宽度
HALF_SCREEN_WIDTH = SCREEN_WIDTH / 2
MAX_ACCEL = 5.0      # 映射范围：当 accel_y 达到 5.0 (约倾斜30度) 时到达屏幕边缘
SMOOTH_FACTOR = 0.2  # 滤波系数 (0.1-1.0)，越小越平滑但延迟越高

# 状态变量
target_x = HALF_SCREEN_WIDTH // 2
current_smooth_x = HALF_SCREEN_WIDTH // 2
is_controlling = True 
pydirectinput.PAUSE = 0

def on_press(key):
    global is_controlling
    if key == keyboard.Key.space:
        is_controlling = not is_controlling
        print(f"\n状态: {'【已接管】' if is_controlling else '【已释放】'}")

listener = keyboard.Listener(on_press=on_press)
listener.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)

print(f"模式：绝对坐标映射 | 范围：±{MAX_ACCEL} G")

try:
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            raw_msg = data.decode().split('|')
            accel_y = float(raw_msg[1])

            if is_controlling:
                # 1. 将加速度值映射到屏幕百分比 (0.0 到 1.0)
                # 假设 0 是中间，-MAX_ACCEL 是左边缘，+MAX_ACCEL 是右边缘
                # 映射公式：(当前值 + 最大值) / (2 * 最大值)
                ratio = (accel_y + MAX_ACCEL) / (2 * MAX_ACCEL)
                
                # 边界剪裁
                ratio = max(0, min(1, ratio))
                
                # 2. 计算目标像素位置
                target_x = int(ratio * HALF_SCREEN_WIDTH)
                
                # 3. 低通滤波 (防止手抖)
                current_smooth_x = current_smooth_x + (target_x - current_smooth_x) * SMOOTH_FACTOR
                
                pydirectinput.moveTo(int(current_smooth_x), 540)

        except socket.timeout:
            continue
except KeyboardInterrupt:
    listener.stop()