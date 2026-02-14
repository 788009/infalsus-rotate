import socket
import pydirectinput
import time
from pynput import keyboard

# 配置
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
SENSITIVITY = 20
SCREEN_WIDTH = 2880
 
# 状态变量
current_x = SCREEN_WIDTH // 2
is_controlling = True 
   
# 禁用 pydirectinput 默认延迟
pydirectinput.PAUSE = 0

def on_press(key):
    global is_controlling, current_x
    try:
        # 监听空格键
        if key == keyboard.Key.space:
            is_controlling = not is_controlling
            status = "【已开启】" if is_controlling else "【已释放】"
            print(f"\n[{time.strftime('%H:%M:%S')}] 状态变更: {status}")
            
            # 重新开启时，从鼠标当前实际位置开始接管，防止跳变
            if is_controlling:
                current_x = pydirectinput.position()[0]
    except AttributeError:
        pass

# 启动非阻塞按键监听器 
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 设置网络
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)  # 避免 recvfrom 永久阻塞

print(f"[{time.strftime('%H:%M:%S')}] 接收端已启动")
print(f"灵敏度: {SENSITIVITY} | 监听端口: {UDP_PORT}")
print("提示: 按下 [空格] 键切换鼠标控制权")
print("-" * 60)

last_print_time = time.time()
msg_count = 0

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            curr_time = time.time()
            
            raw_msg = data.decode().split('|')
            send_time = float(raw_msg[0])
            gyro_z = float(raw_msg[1])

            if is_controlling:
                # 基于角速度的绝对坐标模拟
                if abs(gyro_z) > 0.0005:
                    current_x -= gyro_z * SENSITIVITY
                
                # 边界约束
                current_x = max(0, min(SCREEN_WIDTH, current_x))
                pydirectinput.moveTo(int(current_x), 540)

            # 监控输出
            msg_count += 1
            if curr_time - last_print_time > 1.0:
                delay = (curr_time - send_time) * 1000
                ctrl_label = "ACTIVE" if is_controlling else "IDLE  "
                print(f"\r状态: {ctrl_label} | 延迟: {delay:5.1f}ms | 坐标: {int(current_x):4d} | 频率: {msg_count}Hz", end="")
                msg_count = 0
                last_print_time = curr_time

        except socket.timeout:
            continue
except KeyboardInterrupt:
    print("\n[退出] 正在关闭...")
    listener.stop()