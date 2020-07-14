#-*- coding:utf-8 -*-
import pymysql as pq
import time


def get_record(id):
    db = pq.connect("localhost", "root", "", "lprs")

    cursor = db.cursor()

    sql= "SELECT * FROM result_record WHERE user_id='"+id+"'"

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(sql)
    # cursor.execute("SELECT VERSION()")

    # 使用 fetchall() 方法获取所有数据.
    data = cursor.fetchall()
    #print("MySQL返回值为 %s" % data)
    db.close()
    return data


def save_record(id,type,result,cost_time):

    db = pq.connect("localhost", "root", "", "lprs")

    cursor = db.cursor()

    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    sql="INSERT INTO result_record VALUES('"+id+"','"+type+"','"+result+"','"+nowtime+"','"+cost_time+"')"
    try:
        cursor.execute(sql)
        db.commit()
        print("记录已同步至数据库。")
    except:
        db.rollback()
        print("数据库存储异常。")
    db.close()



if __name__=='__main__':
    all=get_record("admin1")
    for one in all:
        print (one)
