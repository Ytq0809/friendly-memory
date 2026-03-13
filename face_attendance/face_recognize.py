import cv2
import face_recognition
import numpy as np
from ultralytics import YOLO
from db_utils import MySQLUtils
# 加载YOLOv8人脸检测预训练模型
yolo_face_model = YOLO("yolov8n-face.pt")
def load_all_face_encodings():
    """从数据库加载所有用户的人脸特征，用于实时对比"""
    db = MySQLUtils()
    users = db.query_all("SELECT user_id,user_name,user_no,face_encoding FROM user_info")
    db.close()

    if not users:
        return [],[],[],[]

    # 解析二进制特征为numpy数组
    face_encodings = []
    user_ids,user_names,user_nos = [],[],[]
    for user in users:
        face_encoding = np.frombuffer(user["face_encoding"], dtype=np.float64)
        face_encodings.append(face_encoding)
        user_ids.append(user["user_id"])
        user_names.append(user["user_name"])
        user_nos.append(user["user_no"])

    return face_encodings,user_ids,user_names,user_nos
def recognize_face(frame,known_face_encodings,known_user_ids,known_user_names,known_user_nos,tolerance=0.4):
    """
    实时人脸检测与识别
    :param frame: OpenCV读取的视频帧
    :param tolerance: 比对阀值，越小越严格，0.4为工业级通用阀值
    :return: 渲染后的画面、识别到的用户信息
    """
    show_frame = frame.copy()
    rgb_frame = frame[:, :, ::-1].astype("uint8")
    recognized_user = None

    # 1. YOLOv8人脸检测，比传统方法速度更快、准确率更高、适配实时视频流
    results = yolo_face_model(rgb_frame,verbose=False)
    # 提取人脸框坐标，转为face_recognition要求的格式
    face_locations = []
    for result in results:
        for box in result.boxes:
            x1,y1,x2,y2 = map(int,box.xyxy[0])
            face_locations.append((y1,x2,y2,x1))
    # 2. 提取人脸特征
    face_encodings = face_recognition.face_encodings(rgb_frame,face_locations)

    # 3. 与数据库特征对比
    for (top,right,bottom,left),face_encodings in zip(face_locations,face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings,face_encodings,tolerance=tolerance)
        face_distances = face_recognition.face_distance(known_face_encodings,face_encodings)

        name = "未知人员"
        user_id,user_no = None,None

        # 找到相似度最高的匹配
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                user_id = known_user_ids[best_match_index]
                name = known_user_names[best_match_index]
                user_no = known_user_nos[best_match_index]
                recognized_user = {"user_id":user_id,"user_no":user_no,"user_name":name}

        # 4. 画面渲染：画人脸框和姓名
        cv2.rectangle(show_frame,(left,top),(right,bottom),(0,255,0),2)
        cv2.rectangle(show_frame,(left,bottom - 35),(right,bottom),(0,255,0),cv2.FILLED)
        cv2.putText(show_frame,name,(left + 6,bottom - 6),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),1)

    return show_frame,recognized_user
# 测试：运行该文件，验证人脸检测与识别效果
if __name__ == '__main__':
    known_encodings,known_ids,known_names,known_nos = load_all_face_encodings()
    if not known_encodings:
        print("数据库中无录入人脸，请先运行face_register.py录入")
        exit()

    cap = cv2.VideoCapture(0)
    print("摄像头已打开，按'q'键退出")

    while True:
        ret,frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        show_frame,user = recognize_face(frame,known_encodings,known_ids,known_names,known_nos)
        cv2.imshow("Face Recognition",show_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()