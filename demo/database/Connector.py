import re

import pymysql


def table_exists(con, table_name) -> bool:  # 这个函数用来判断表是否存在
    sql = "show tables;"
    con.execute(sql)
    tables = [con.fetchall()]
    print(tables)
    table_list = re.findall('(\'.*?\')', str(tables))
    print(table_list)
    table_list = [re.sub("'", '', each) for each in table_list]
    if table_name in table_list:
        return True  # 存在返回1
    else:
        return False  # 不存在返回0


conn = db = pymysql.connect(host="localhost", port=3306, user='subadmin', password='subadmin', database='test')
cursor = conn.cursor()
# 创建user表:
if not table_exists(cursor, "user"):
    cursor.execute('create table if not exists user (id varchar(20) primary key, name varchar(20))')
# 插入一行记录，注意MySQL的占位符是%s:
#cursor.execute('insert into user (id, name) values (%s, %s)', ['5', 'Michael'])
#print(cursor.rowcount)
# 提交事务:
conn.commit()
cursor.close()
# 运行查询:
cursor = conn.cursor()
cursor.execute('select * from user where id = %s', ('1',))
values = cursor.fetchall()
print(values)
print(type(values))
for i in values:
    for j in i:
        print(type(i))
        print(j)
# 关闭Cursor和Connection:
cursor.close()
conn.close()
