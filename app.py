from flask import Flask, request
from time import time, sleep
from threading import Thread
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Replace the database URI with your actual PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tztvvsuw:wUGjVSR5Yutc4eIHGHPqmwBRgA_A9Ify@satao.db.elephantsql.com/tztvvsuw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), unique=True, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)

# Create the table if it doesn't exist
db.create_all()

@app.route('/')
def home():
    ip = request.args.get('ip')
    if not ip:
        return "<h1>Insert IP in url parameter as `ip=0.0.0.0`</h1>"

    # Check if the IP exists in the database
    ip_obj = IPAddress.query.filter_by(ip_address=ip).first()

    if ip_obj:
        return 'false'
    else:
        # Insert the IP into the database
        timestamp = time()
        new_ip = IPAddress(ip_address=ip, timestamp=timestamp)
        db.session.add(new_ip)
        db.session.commit()
        return 'true'

def background_task():
    while True:
        # Remove IP addresses that have been stored for more than 24 hours
        current_time = time()
        old_ips = IPAddress.query.filter((current_time - IPAddress.timestamp) > (24 * 60 * 60)).all()

        for ip in old_ips:
            db.session.delete(ip)
        db.session.commit()
        sleep(60 * 30)

t = Thread(target=background_task)
t.daemon = True
t.start()

if __name__ == '__main__':
    app.run('0.0.0.0', 80, True)
