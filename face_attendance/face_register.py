import cv2
import face_recognition
from db_utils import MySQLUtils
def register_face(user_name,user_no):
    """人脸录入：采集人脸——>提取特征——>存入数据库"""
    db = MySQLUtils()
    # 检验工号是否重复
    exist_user = db.query_one("SELECT * FROM user_info WHERE user_no = %s",args=(user_no,))
    if exist_user:
        print(f"错误：工号:{user_no}已存在，请勿重复录入")
        db.close()
        return

    # 打开默认摄像头
    cap = cv2.VideoCapture(0)
    print("摄像头已打开，请正对摄像头，按‘s’键保存人脸，按‘q'键退出")

    face_encoding = None
    while True:
        # 读取摄像头画面
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break
        # 实时显示画面
        cv2.imshow("Face Register",frame)
        # 监听按键
        key = cv2.waitKey(1) & 0xFF
        # 按s键保存人脸
        if key == ord('s'):
            # 使用 cv2.cvtColor 生成连续的 RGB 数组
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 检测人脸位置
            face_locations = face_recognition.face_locations(rgb_frame)
            # 提取人脸特征编码
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # 异常检验
            if len(face_encodings) == 0:
                print("未检验到人脸，请正对摄像头重试")
            elif len(face_encodings) > 1:
                print("检验到多个人脸，请保证画面中只有你一个")
            else:
                face_encoding = face_encodings[0]
                print("人脸特征提取成功")
                break
        # 按q键退出
        elif key == ord('q'):
            print("取消录入")
            cap.release()
            cv2.destroyAllWindows()
            db.close()
            return
    # 释放摄像头
    cap.release()
    cv2.destroyAllWindows()
    # 特征转为二进制，存入MySQL的BLOB字段
    if face_encoding is not None:
        face_encoding_blob = face_encoding.tobytes()
        # 插入用户数据
        insert_sql = """
        INSERT INTO user_info(user_name,user_no,face_encoding)
        VALUES(%s,%s,%s)
        """
        rows = db.execute(insert_sql,args=(user_name,user_no,face_encoding_blob))

        if rows > 0:
            print(f"用户{user_name}(工号：{user_no}) 人脸录入成功")
        else:
            print("人脸录入失败")
    else:
        print("未成功提取人脸特征，录入终止")
    db.close()
# 测试：运行该文件，修改姓名和工号，即可录入人脸
if __name__ == "__main__":
    register_face(user_name="闫天秋",user_no="20010809")