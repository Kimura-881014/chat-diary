import csv
import os
from datetime import datetime
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatdiary.settings.development')
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


with open('./beta-data.csv',encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        print(row)
        user_id = row[0]
        date_string = row[1] + ' ' +'00:00:00'
        parsed_datetime = datetime.strptime(date_string, "%Y.%m.%d %H:%M:%S")
        aware_datetime = timezone.make_aware(parsed_datetime, timezone.get_current_timezone())
        # print(aware_datetime)
        title = row[2]
        body = row[3]
        chat_type=1
        release = False
        sql = f'INSERT INTO diary_data\
            (user_id, posted_date, title, body, chat_type, release)\
                VALUES\
                    ({user_id},{aware_datetime},{title},{body},{chat_type},{release});'
        print(sql)
        # SQL実行
        cursor.execute(sql)
        break

conn.commit()
# 接続を閉じる
cursor.close()
conn.close()

# # 文字列からdatetimeオブジェクトを作成
# date_string = "2024-02-14 12:30:00"
# parsed_datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

# # datetimeをDjangoのtimezoneに変換 (タイムゾーンを設定)
# aware_datetime = timezone.make_aware(parsed_datetime, timezone.get_current_timezone())

# # 結果の表示
# print("Parsed datetime:", parsed_datetime)
# print("Aware datetime:", aware_datetime)