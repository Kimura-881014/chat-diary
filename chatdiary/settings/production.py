from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # sqliteから変更
        'NAME': 'chat_diary',     # プロジェクト用に作成したデータベース名
        'USER': os.environ['MYSQL_USER'],   # RDSで作成したユーザー名
        'PASSWORD': os.environ['MYSQL_PASSWORD'],    # RDSで作成したユーザーのパスワード
        'HOST': os.environ['MYSQL_HOST'],
        'PORT': '3306',
    }
}