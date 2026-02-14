# In Falsus Rotate

基于手机旋转角度的 [In Falsus](https://infalsus.lowiro.com/) 天键解决方案，加速度计方案的实际效果参考[这个视频](https://www.bilibili.com/video/BV1khcnz1ENa/)。

## 使用方法

目前实现了两种方案，陀螺仪（gyroscope）和加速度计（accelerometer），都需要在手机和电脑上同时运行脚本，其中手机发送数据，电脑接收数据并操控鼠标。

手机与电脑应处于同一局域网下，并可以通过局域网通信。

> [!NOTE]
>
> 由于程序只对我自己的设备进行了配置与优化，这里不提供二进制文件，你很可能需要直接修改代码内容（不仅仅是开头的配置）来获得最佳体验。

### 电脑

克隆本仓库并安装依赖。

```bash
git clone https://github.com/788009/infalsus-rotate.git
cd infalsus-rotate
pip install -r requirements.txt
```

> [!IMPORTANT]
> 
> 运行之前，请务必打开 `{approach}-pc.py` 查看开头的配置并按需修改。

运行程序。

```bash
# 陀螺仪
python gyroscope-pc.py
# 加速度计
python accelerometer-pc.py
```

### 手机

手机操作全部在 [Termux](https://github.com/termux/termux-app) 内进行。

安装 Python。

```bash
pkg update
pkg install python
```

使用 Git 或其他方式将 `{approach}-phone.py` 放在 Termux 可访问的目录。

#### 获取传感器名称

查看传感器列表。

```bash
termux-sensor -l
```

一般来说，陀螺仪的名字包含 `Gyro`，而加速度计的名字包含 `Acce`，比如在我的设备上

```bash
termux-sensor -l | grep Gyro
# 输出
    "bmi26x Gyroscope Non-wakeup",
    "bmi26x Gyroscope-Uncalibrated Non-wakeup",
```

其中 `-Uncalibrated` 指的是未校准，因此请使用不带 `-Uncalibrated` 的传感器。

不同型号的手机传感器名称不尽相同，若找不到请自行根据型号搜索。

#### 运行程序

首先，编辑 `{approach}-phone.py`，修改开头的配置，包括电脑 IP `COMPUTER_IP` 和传感器名称 `SENSOR_NAME`。

尝试运行。

```bash
# 陀螺仪
python gyroscope-phone.py
# 加速度计
python accelerometer-phone.py
```

可能需要等待一段时间（小于一分钟）电脑上才会有反应。

若电脑上鼠标始终没有反应或者行为怪异，大概率是因为你的传感器输出格式与代码预设的不同，请自行分析并修改双端代码。

### 注意事项

在游戏内，手机水平不一定一开始就映射到屏幕中心，此时可以用鼠标或触控板移动光标来校准。

按下空格即可自由移动鼠标，再次按下恢复手机旋转控制。

## 原理与评价

手机上使用 `termux-sensor` 命令实时获取手机旋转角度并通过 UDP 发送给电脑，电脑将其映射到光标位置。

### 陀螺仪

- 优点：既可以像 Rotaeno 一样手持，也可以平放在桌面旋转。
- 缺点：目前我只能通过陀螺仪获取手机在三个方向旋转的角速度，因此只能映射到鼠标移动的速度，鼠标移动到边缘后无法继续移动，但手机可以继续旋转，而手机转向反方向旋转时鼠标会立刻开始移动，导致中心点偏移。
    - 有尝试过手动维护溢出值，但在游戏内行为比较诡异，遂放弃。
    - 还尝试过一个叫做 `Rotation Vector` 的传感器，可以获取手机的绝对旋转角度，但获取频率太低，实际效果非常卡，遂放弃。

### 加速度计

- 优点：获取的加速度值直接对应手机旋转角度，因此可以映射到光标的绝对位置，中心点永远不会偏移。
- 缺点：只能像 Rotaeno 一样手持，无法平放在桌面旋转。

总体来说，不管是陀螺仪还是加速度计，虽然看着电脑屏幕操作时效果都不错，但在与串流配合时均不如[头部追踪方案](https://github.com/788009/infalsus-head-tracker)（你还得打地键，对吧）~~，或许可以作为双人游玩的一个可行方案~~。

## 许可证

MIT License