#-*- coding:utf-8 -*-
import pymysql as pq
import time


def connect_check():
    db = pq.connect("localhost", "root", "", "lprs")
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    #使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    print("MySQL版本为 %s" % data)
    db.close()

def login_check(id,password):
    db = pq.connect("localhost", "root", "", "lprs")

    cursor = db.cursor()

    sql= "SELECT * FROM user_info WHERE id='"+id+"'AND password='"+password+"'"

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(sql)
    # cursor.execute("SELECT VERSION()")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    #print("MySQL返回值为 %s" % data)
    db.close()
    if data is None:
        return False
    else:
        return True

def register_check(id,password):
    success="注册成功"
    err1="用户名和密码不能为空！"
    err2="用户名已存在！"
    if id == "" or password == "":
        return False,err1

    db = pq.connect("localhost", "root", "", "lprs")

    cursor = db.cursor()

    sql= "SELECT * FROM user_info WHERE id='"+id+"'"

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(sql)
    # cursor.execute("SELECT VERSION()")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()

    if data is None:
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql="INSERT INTO user_info VALUES('"+id+"','"+password+"','"+nowtime+"')"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()
        return True,success
    else:
        db.close()
        return False,err2


if __name__=='__main__':
    #login_check("qqq","123")
    connect_check()
