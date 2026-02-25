import cv2
import numpy as np
from IPython.display import display, clear_output
from PIL import Image
import time

# 1. 强制Qt使用X11后端，解决Wayland兼容性问题
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

# 2. 加载人脸检测分类器
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 3. 尝试打开摄像头（优先尝试索引1，也可以尝试0或-1）
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("错误：无法打开摄像头！请检查：")
    print("1. 摄像头是否已连接到虚拟机（VMware -> 可移动设备）")
    print("2. 当前用户是否在video组中（sudo usermod -aG video $USER）")
    print("3. 尝试更换摄像头索引（0, 1, -1）")
else:
    print("提示：运行后，点击Kernel -> Interrupt 退出程序")
    try:
        while True:
            # 读取摄像头帧
            ret, frame = cap.read()
            if not ret:
                break
            # 转为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 检测人脸
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            # 绘制人脸检测框
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # 将BGR格式转为RGB，以便在Jupyter中显示
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            # 清屏并显示新帧
            clear_output(wait=True)
            display(img)
            # 控制帧率，避免CPU占用过高
            time.sleep(0.03)
    except KeyboardInterrupt:
        print("\n程序已手动中断")
    finally:
        # 释放资源
        cap.release()
        print("摄像头资源已释放")
