from datetime import time
import time
import cv2
from face_recognize import load_all_face_encodings,recognize_face
from attendance_core import add_attendance_record
def main():
    # 1. 加载人脸数据库
    print("正在加载人脸数据库...")
    known_encodings,known_ids,known_names,known_nos = load_all_face_encodings()
    if not known_encodings:
        print("错误：数据库中无录入人脸，请先运行face_register.py录入")
        return
    print(f"人脸数据库加载完成，共加载{len(known_encodings)}个用户")

    # 2. 打开摄像头，设置分辨率
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("摄像头已打开，系统启动成功")
    print("操作说明：按'i'键切换上班/下班打卡，按'q'键退出系统")
    # 初始化打卡类型
    checkin_type = "上班打卡"
    # 记录上次打卡时间戳
    last_checkin_time = 0
    while True:
        # 读取视频帧
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面，系统退出")
            break
        # 人脸检测与识别
        show_frame,recognized_user = recognize_face(frame,known_encodings,known_ids,known_names,known_nos)
        # 画面显示当前打卡类型
        cv2.putText(show_frame,f"当前类型：{checkin_type}",(20,50),cv2.FONT_HERSHEY_DUPLEX,1,(0,0,255),2)

        # 增加打卡时间
        current_time = time.time()
        if current_time - last_checkin_time < 5:
            # 5秒内不重复打卡
            continue  # 跳过本次打卡逻辑

        # 识别到用户自动打卡
        if recognized_user:
            add_attendance_record(recognized_user,checkin_type)

        # 更新打卡时间
        last_checkin_time = current_time

        # 显示画面
        cv2.imshow("智能人脸考勤系统",show_frame)
        # 按键监听
        key = cv2.waitKey(1) & 0xFF
        if key == ord('i'):
            checkin_type = "下班打卡" if checkin_type == "上班打卡" else "上班打卡"
            print(f"已切换为:{checkin_type}")
        elif key == ord('q'):
            print("正在退出系统...")
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()
