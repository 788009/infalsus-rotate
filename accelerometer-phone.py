import subprocess
import socket
import json
import time

# 配置
COMPUTER_IP = "192.168.1.50"
UDP_PORT = 5005
SENSOR_NAME = "bmi26x Accelerometer Non-wakeup"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绝对坐标映射建议保持 50Hz-100Hz 以获得丝滑感
cmd = ["termux-sensor", "-s", SENSOR_NAME, "-d", "10"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

print(f"[{time.strftime('%H:%M:%S')}] 手机发送端 (绝对映射模式) 启动")

buffer = ""
try:
    for line in process.stdout:
        buffer += line.strip()
        if "}" in line and buffer.count('{') == buffer.count('}'):
            try:
                data = json.loads(buffer)
                if SENSOR_NAME in data:
                    # values[1] 是手机长轴的倾斜 (G力分量)
                    accel_y = data[SENSOR_NAME]["values"][1]
                    msg = f"{time.time()}|{accel_y}"
                    sock.sendto(msg.encode(), (COMPUTER_IP, UDP_PORT))
                buffer = ""
            except:
                buffer = ""
except KeyboardInterrupt:
    process.terminate()