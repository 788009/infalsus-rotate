import subprocess
import socket
import json
import time

# 配置
COMPUTER_IP = "192.168.162.39"
UDP_PORT = 5005
SENSOR_NAME = "bmi26x Gyroscope Non-wakeup"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 使用 -d 10 (100Hz) 保证高刷新率
cmd = ["termux-sensor", "-s", SENSOR_NAME, "-d", "10"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

print(f"[{time.strftime('%H:%M:%S')}] 手机发送端启动")
print(f"目标电脑: {COMPUTER_IP} | 传感器: {SENSOR_NAME}")

buffer = ""
count = 0
try:
    for line in process.stdout:
        buffer += line.strip()
        if "}" in line and buffer.count('{') == buffer.count('}'):
            try:
                data = json.loads(buffer)
                if SENSOR_NAME in data:
                    gyro_val = data[SENSOR_NAME]["values"][2] # Z轴
                    # 发送格式: 时间戳|数值
                    msg = f"{time.time()}|{gyro_val}"
                    sock.sendto(msg.encode(), (COMPUTER_IP, UDP_PORT))

                    count += 1
                    if count % 100 == 0: # 每发100条输出一次状态
                        print(f"\r已发送 {count} 条数据 | 最新值: {gyro_val:.4f}", end="")
                buffer = ""
            except:
                buffer = ""
except KeyboardInterrupt:
    print("\n[退出] 正在清理传感器...")
    process.terminate()