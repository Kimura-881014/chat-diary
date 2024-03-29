FROM python:3.8
ENV PYTHONUNBUFFERED 1
#この環境変数に値を入れることでバッファを無効化する('1'じゃなくてもいい)
RUN mkdir /code
# codeディレクトリを作成
WORKDIR /code
# codeディレクトリに移動
COPY requirements.txt /code/
# txtファイルをcodeディレクトリに配置
ADD wsgi.conf /etc/apache2/sites-available/wsgi.conf
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y apache2 apache2-dev default-mysql-client
RUN pip install mod_wsgi

# pipコマンドを最新にし、txtファイル内のパッケージ（後述）をpipインストール
COPY . /code/
# sample-pj/配下のファイルをcodeディレクトリにコピー

RUN a2dissite 000-default
RUN a2ensite wsgi
# RUN service apache2 restart