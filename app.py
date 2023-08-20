from flask import Flask, request, make_response
from time import time, sleep
from threading import Thread
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tztvvsuw:wUGjVSR5Yutc4eIHGHPqmwBRgA_A9Ify@satao.db.elephantsql.com/tztvvsuw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), unique=True, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)


with app.app_context(): db.create_all()

data={'duplicate':0}

@app.route('/')
def home():
    ip = request.args.get('ip')
    if not ip:
        return f"<h1>Insert IP in url parameter as `ip=0.0.0.0` to endpoints '/isnew' and '/add' and to see all use '/used' and to remove one use '/del'</h1><br><br><h3>duplicate: {data['duplicate']}</h3>"

    ip_obj = IPAddress.query.filter_by(ip_address=ip).first()

    if ip_obj:
        return 'false'
    else:
        timestamp = time()
        new_ip = IPAddress(ip_address=ip, timestamp=timestamp)
        db.session.add(new_ip)
        db.session.commit()
        with open('ip', 'a+') as file:
            file.write(ip + '\n')
        return 'true'

@app.route('/isnew')
def isnew_route():
    ip = request.args.get('ip')
    ip_obj = IPAddress.query.filter_by(ip_address=ip).first()
    if ip_obj:
        return 'false'
    else:
        return 'true'

@app.route('/add')
def add_route():
    ip = request.args.get('ip')
    ip_obj = IPAddress.query.filter_by(ip_address=ip).first()
    if not ip_obj:
        timestamp = time()
        new_ip = IPAddress(ip_address=ip, timestamp=timestamp)
        db.session.add(new_ip)
        db.session.commit()
        with open('ip', 'a+') as file:
            file.write(ip + '\n')
    else:
        data['duplicate']+=1
    return 'true'

@app.route('/del')
def delete_route():
    ip = request.args.get('ip')
    ip_obj = IPAddress.query.filter_by(ip_address=ip).first()
    if ip_obj:
        db.session.delete(ip_obj)
        db.session.commit()
    with open('ip', 'r') as file:
        file_content = file.read()
    with open('ip', 'w') as file:
        file.write(file_content.replace(f'{ip}\n',''))
    return 'true'

@app.route('/used')
def used_route():
    with open('ip', 'r') as file:
        text = file.read()
    r = make_response(text, 200)
    r.mimetype = 'text/plain;charset=UTF-8'
    return r


def background_task():
    while True:
        with app.app_context():
            current_time = time()
            old_ips = IPAddress.query.filter((current_time - IPAddress.timestamp) > (24 * 60 * 60)).all()

            for ip in old_ips:
                db.session.delete(ip)
            db.session.commit()
        sleep(60 * 30)

def background_task2():
    while True:
        with open('ip', 'w') as file:
            with app.app_context():
                all_ip = IPAddress.query.all()
                for ip in all_ip:
                    file.write(ip.ip_address + '\n')
        sleep(60 * 15)


t1 = Thread(target=background_task)
t1.daemon = True
t1.start()

t2 = Thread(target=background_task2)
t2.daemon = True
t2.start()

if __name__ == '__main__':
    app.run('0.0.0.0', 80, True)
