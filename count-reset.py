import os
import mysql.connector
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# MySQLに接続
conn = mysql.connector.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database='chat_diary',
        port="3306",
        )

# カーソルを取得
cursor = conn.cursor()

# SQL文
sql = "UPDATE chat_tmpmsg SET count=0;"

# SQL実行
cursor.execute(sql)
conn.commit()

# 接続を閉じる
cursor.close()
conn.close()