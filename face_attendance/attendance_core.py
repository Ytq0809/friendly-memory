from datetime import datetime,time
from db_utils import MySQLUtils
# 考勤时间配置，可自行修改
WORK_CONFIG = {
    "morning_start": time(9,0),   # 上班时间
    "morning_late": time(9,30),   # 迟到判定时间
    "evening_start": time(18,0),  # 下班时间
    "evening_early": time(17,30), # 早退判定时间
}
def check_duplicate_checkin(user_id,checkin_type):
    """校验重复打卡：统一用户同一天同一类型只能打一天"""
    db = MySQLUtils()
    today = datetime.now().date()
    sql = """
    SELECT * FROM attendance_record
    WHERE user_id = %s AND checkin_time = %s AND DATE(checkin_time) = %s
    """
    record = db.query_one(sql,args=(user_id,checkin_type,today))
    db.close()
    return record is not None
def get_checkin_status(checkin_type):
    """根据当前时间判定打卡状态（正常/迟到/早退）"""
    now_time = datetime.now().time()
    status = "正常"
    if checkin_type == "上班打卡" and now_time > WORK_CONFIG["morning_start"]:
        status = "迟到"
    elif checkin_type == "下班打卡" and now_time < WORK_CONFIG["evening_early"]:
        status = "早退"
    return status
def add_attendance_record(user_info,checkin_type="上班打卡"):
    """添加考勤记录到数据库，返回打卡结果"""
    user_id = user_info["user_id"]
    user_name = user_info["user_name"]
    user_no = user_info["user_no"]

    # 重复打卡拦截
    if check_duplicate_checkin(user_id,checkin_type):
        print(f"用户{user_name}今日已打过{checkin_type}，请勿重复打卡")
        return False
    # 获取打卡状态
    status = get_checkin_status(checkin_type)
    # 插入打卡记录
    db = MySQLUtils()
    insert_sql = """
    INSERT INTO attendance_record(user_id, user_name, user_no,checkin_type,status)
    VALUES(%s,%s,%s,%s,%s)
    """
    rows = db.execute(insert_sql,args=(user_id,user_name,user_no,checkin_type,status))
    db.close()

    if rows > 0:
        print(f"打卡成功！用户:{user_name},类型:{checkin_type},状态:{status},时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    else:
        print("打卡失败")
        return False

# 测试：运行该文件，验证打卡功能
if __name__ == "__main__":
    test_user = {"user_id":1,"user_name":"闫天秋","user_no":"20010809"}
    add_attendance_record(test_user,checkin_type="上班打卡")