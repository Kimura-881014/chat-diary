import csv
import os
from datetime import datetime
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatdiary.settings.production')
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

user_list = []

# sql = "SELECT `password` FROM accounts_user WHERE id=2;"
# cursor.execute(sql)
# password = cursor.fetchall()[0][0]
# # print(rows)
# cursor.close()
cursor = conn.cursor()

with open('./beta-data.csv',encoding="utf-8") as f:

    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        # print(row)
        user_id = str(row[0])
        chat_type = 1
        if user_id not in user_list:
            print('here')
            password = "initialtestpassword"
            sql = "INSERT INTO accounts_user (user_id,`email`, `password`) VALUES (%(user_id)s, %(email)s, %(password)s);"
            values = {'user_id':user_id, 'email':"",'password':password}
            cursor.execute(sql, values)
            conn.commit()
            print("user ok")
            sql = "INSERT INTO chat_tmpmsg (user_id, count, title, body, question,chat_type_id,body_payload,question_payload) VALUES ((SELECT id FROM accounts_user WHERE user_id = %(user_id)s), %(count)s, %(title)s, %(body)s, %(question)s,(SELECT id FROM chat_chattype WHERE id = %(chat_type)s), %(body_payload)s,%(question_payload)s);"
            values = {'user_id':user_id, 'count':0,'title':"",'body':"",'question':"","chat_type":chat_type,'body_payload':"",'question_payload':""}
            cursor.execute(sql, values)
            user_list.append(user_id)
            conn.commit()
            print("tmpmsg ok")

        date = str(row[1] + ' ' + '00:00:00')
        date = datetime.strptime(date, "%Y.%m.%d %H:%M:%S")
        datetime = timezone.make_aware(date, timezone.get_current_timezone())
        title = str(row[2])
        body = str(row[3])
        # release = False

        # SQLクエリ内の値を正しくフォーマット
        sql = "INSERT INTO diary_data (user_id, posted_date, title, body, chat_type_id) VALUES ((SELECT id FROM accounts_user WHERE user_id = %(user_id)s), %(posted_date)s, %(title)s, %(body)s, (SELECT id FROM chat_chattype WHERE id = %(chat_type)s));"
        values = {'user_id':user_id, 'posted_date':date,'title': title,'body': body,'chat_type': chat_type}
        print(sql)
        # SQL実行
        cursor.execute(sql, values)
        break


conn.commit()
# 接続を閉じる
cursor.close()
conn.close()