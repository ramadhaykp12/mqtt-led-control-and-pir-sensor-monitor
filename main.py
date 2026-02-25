import network
import time
from machine import Pin
from umqtt_simple import MQTTClient

# Konfigurasi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "pico_w_iot_hub"
TOPIC_PIR = b"rumah/sensor/pir"
TOPIC_LED = b"rumah/lampu/kontrol"

# Setup Pin
pir = Pin(13, Pin.IN)
led = Pin(12, Pin.OUT)

# Fungsi Callback untuk menerima perintah LED
def sub_cb(topic, msg):
    print(f"Perintah diterima pada {topic}: {msg}")
    if msg == b"ON":
        led.value(1)
    elif msg == b"OFF":
        led.value(0)

# Koneksi Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(1)

# Koneksi MQTT
client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.set_callback(sub_cb)
client.connect()
client.subscribe(TOPIC_LED)

print("Sistem Aktif. Menunggu sensor dan perintah...")

last_pir_state = 0

while True:
    # 1. Cek Sensor PIR (Publisher)
    current_pir_state = pir.value()
    if current_pir_state != last_pir_state:
        msg = b"GERAKAN" if current_pir_state == 1 else b"AMAN"
        client.publish(TOPIC_PIR, msg)
        print(f"Status Sensor: {msg}")
        last_pir_state = current_pir_state
    
    # 2. Cek pesan masuk (Subscriber)
    client.check_msg() 
    
    time.sleep(0.1)
