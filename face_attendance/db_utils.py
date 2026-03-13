import pymysql
from pymysql.cursors import DictCursor
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ytq20010809@',
    'database':'face_attendance',
    'charset':'utf8mb4'
}
class MySQLUtils:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
    def connect(self):
        """连接数据库，加入异常处理"""
        try:
            self.conn = pymysql.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(DictCursor) # 返回字典格式，方便取值
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败:{e}")
    def execute(self,sql,args=None):
        """执行增删改SQL，带事务回滚"""
        try:
            rows = self.cursor.execute(sql,args)
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            print(f"SQL执行失败:{e}")
            return 0
    def query_one(self,sql,args=None):
        """查询单条数据"""
        try:
            self.cursor.execute(sql,args)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"查询失败:{e}")
            return None
    def query_all(self,sql,args=None):
        """查询多条数据"""
        try:
            self.cursor.execute(sql,args)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败:{e}")
            return None
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("数据库连接已关闭")
# 测试：运行该文件，验证数据库是否连接成功
if __name__ == "__main__":
    db = MySQLUtils()
    db.close()