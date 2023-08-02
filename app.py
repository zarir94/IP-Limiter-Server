from flask import Flask, request
from time import time, sleep
from threading import Thread

app=Flask(__name__)
app.config['SECRET_KEY']='thisIsMySecretKey'

all_ip = {}

@app.route('/')
def home():
    ip = request.args.get('ip')
    if not ip:
        return "<h1>Insert IP in url parameter as `ip=0.0.0.0`</h1>"
    if all_ip.get(ip):
        return 'false'
    else:
        all_ip[ip] = time()
        return 'true'
    
def background_task():
    while True:
        for ip in list(all_ip):
            if (time() - all_ip[ip]) > (24 * 60 * 60):
                del all_ip[ip]
        sleep(60 * 30)

t=Thread(target=background_task)
t.daemon=True
t.start()

if __name__ == '__main__':
    app.run('0.0.0.0', 80, True)

