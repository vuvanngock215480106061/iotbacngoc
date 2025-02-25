from flask import Flask, request, render_template, jsonify
import sqlite3
import requests
from flask_cors import CORS
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app)

#  múi giờ Việt Nam (UTC+7)
LOCAL_TZ = timezone(timedelta(hours=7))

#  Token bot Telegram và chat ID của bạn
TELEGRAM_BOT_TOKEN = '7703022331:AAGY4VZGWJeyK9Gq2-BcGEiY1qV1arvxgPU'
TELEGRAM_CHAT_ID = '6292290303'


#  Hàm gửi tin nhắn qua Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)

    # Thêm log để kiểm tra phản hồi
    if response.ok:
        print("📡 Đã gửi tin nhắn Telegram thành công!")
    else:
        print(f"❌ Lỗi gửi tin nhắn: {response.json()}")
        print(f"Chi tiết lỗi: {response.text}")  # Xem chi tiết phản hồi lỗi từ Telegram API


#  Hàm chuyển timestamp từ UTC sang giờ địa phương
def convert_to_localtime(timestamp_str):
    if timestamp_str:
        utc_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        local_time = utc_time.astimezone(LOCAL_TZ)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')
    return None


#  Khởi tạo database SQLite
def init_db():
    with sqlite3.connect('sensor_data.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        temperature REAL,
                        humidity REAL,
                        timestamp DATETIME DEFAULT (datetime('now'))
                    )''')
        conn.commit()


# 📌 Hàm lưu dữ liệu vào DB
def save_data_to_db(temperature, humidity, utc_timestamp):
    with sqlite3.connect('sensor_data.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO data (temperature, humidity, timestamp) VALUES (?, ?, ?)",
                  (temperature, humidity, utc_timestamp))
        conn.commit()


@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()
    if data:
        temperature = data.get('temperature')
        humidity = data.get('humidity')

        if temperature is not None and humidity is not None:
            #  Lấy thời gian hiện tại theo UTC để lưu vào DB
            utc_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            save_data_to_db(temperature, humidity, utc_timestamp)

            print(f"📡 Dữ liệu nhận được: Temp={temperature}°C, Hum={humidity}%")

            #  Kiểm tra nếu nhiệt độ > 30°C hoặc độ ẩm > 70% thì gửi tin nhắn Telegram
            if temperature > 30 or humidity > 70:
                message = f"📡 Dữ liệu mới từ cảm biến:\nNhiệt độ: {temperature}°C\nĐộ ẩm: {humidity}%\nThời gian: {convert_to_localtime(utc_timestamp)}"
                send_telegram_message(message)

            return jsonify({"message": "Data received successfully"}), 200
        else:
            return jsonify({"error": "Missing temperature or humidity data"}), 400
    return jsonify({"error": "No data received"}), 400


#  API lấy dữ liệu mới nhất (JSON) và chuyển timestamp về giờ địa phương
@app.route('/api/latest_data', methods=['GET'])
def get_latest_data():
    with sqlite3.connect('sensor_data.db') as conn:
        c = conn.cursor()
        c.execute("SELECT temperature, humidity, timestamp FROM data ORDER BY timestamp DESC LIMIT 10")
        rows = c.fetchall()

    #  Chuyển timestamp về giờ địa phương
    data = [{"temperature": row[0], "humidity": row[1], "timestamp": convert_to_localtime(row[2])} for row in rows]
    return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    init_db()  # Tạo database
    app.run(host='0.0.0.0', port=5000, debug=True)
