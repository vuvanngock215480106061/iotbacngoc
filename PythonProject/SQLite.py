import sqlite3

conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()

# Xóa toàn bộ dữ liệu trong bảng
c.execute("DELETE FROM data")
conn.commit()
conn.close()

print("✅ Đã xóa toàn bộ dữ liệu trong bảng data.")
