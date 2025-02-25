#include <WiFi.h>            // Dùng ESP32, nếu ESP8266 thì dùng <ESP8266WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <stdlib.h>           // Thư viện sinh số ngẫu nhiên

const char* ssid = "Bac";        // Nhập tên WiFi
const char* password = "thangmatlon1";    // Nhập mật khẩu WiFi
const char* server = "http://172.20.10.12:5000/api/sensor_data";  // Flask server

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    Serial.print("Đang kết nối WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nWiFi đã kết nối!");

    // Khởi tạo seed cho số ngẫu nhiên
    randomSeed(analogRead(0));
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        float temperature = random(200, 350) / 10.0;  // Giả lập nhiệt độ từ 20.0°C - 35.0°C
        float humidity = random(300, 700) / 10.0;     // Giả lập độ ẩm từ 30.0% - 70.0%

        Serial.printf("📡 Gửi: Temp=%.2f°C, Hum=%.2f%%\n", temperature, humidity);
        
        HTTPClient http;
        http.begin(server);
        http.addHeader("Content-Type", "application/json");

        StaticJsonDocument<200> json;
        json["temperature"] = temperature;
        json["humidity"] = humidity;

        String jsonStr;
        serializeJson(json, jsonStr);
        int httpResponseCode = http.POST(jsonStr);

        Serial.printf("📨 Phản hồi server: %d\n", httpResponseCode);
        http.end();
    } else {
        Serial.println("⚠️ Mất kết nối WiFi! Đang thử kết nối lại...");
        WiFi.disconnect();
        WiFi.reconnect();
    }

    delay(5000);  // Gửi dữ liệu mỗi 5 giây
}
