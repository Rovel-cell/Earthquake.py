import time
import smbus2
from mpu6050 import mpu6050
import adafruit_ds3231
import board
import busio
import requests
import pygame
from datetime import datetime

# Initialize I2C for MPU6050 (accelerometer/gyro) and DS3231 (clock)
i2c = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_ds3231.DS3231(i2c)
sensor = mpu6050(0x68)

# Your Mailgun API credentials
MAILGUN_API_KEY = '94cc7bc5fc2cebc64b114c75807fd8ca'
MAILGUN_DOMAIN = 'your-domain.mailgun.org'
SMS_RECIPIENTS = [
    '09988050681', '09942598558', '09682977115',
    '09461038863', '09532963173', '09810403192'
]

# Threshold for earthquake magnitude (4.5 and above)
EARTHQUAKE_THRESHOLD = 4.5

# Audio alert file (a .wav file of your choice)
ALERT_SOUND = "earthquake_alert.wav"

# Function to send SMS using Mailgun
def send_sms_alert(message):
    print("Sending SMS alert...")
    for recipient in SMS_RECIPIENTS:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={"from": "Earthquake Alert <mailgun@your-domain.com>",
                  "to": recipient,
                  "subject": "Earthquake Alert!",
                  "text": message})
        if response.status_code == 200:
            print(f"Alert sent to {recipient}")
        else:
            print(f"Failed to send alert to {recipient}: {response.status_code}")

# Function to play an alert sound
def play_audio_alert():
    pygame.mixer.init()
    pygame.mixer.music.load(ALERT_SOUND)
    pygame.mixer.music.play()

# Function to get current time from DS3231
def get_current_time():
    return rtc.datetime

# Function to check for an earthquake and respond
def check_for_earthquake():
    accel_data = sensor.get_accel_data()
    total_acceleration = (accel_data['x']**2 + accel_data['y']**2 + accel_data['z']**2) ** 0.5
    
    # Simulated formula to convert acceleration to magnitude
    magnitude = total_acceleration / 9.8 * 5.0
    
    if magnitude >= EARTHQUAKE_THRESHOLD:
        current_time = get_current_time()
        alert_message = f"Earthquake detected! Magnitude: {magnitude:.2f}, Time: {current_time}"
        
        print(alert_message)
        send_sms_alert(alert_message)
        play_audio_alert()
    else:
        print("No significant earthquake detected.")

# Main loop to check for earthquakes continuously
if __name__ == "__main__":
    print("Starting earthquake detection system...")
    while True:
        check_for_earthquake()
        time.sleep(2)  # Check every 2 seconds