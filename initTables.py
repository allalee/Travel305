import pymysql as pymysql
import sys

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', db='Travel305', password='password')
cursor = conn.cursor() # Cursor object is what we will use to execute commands

fd = open(sys.argv[1], "r")
for line in fd:
	cursor.execute(line)
conn.commit()
