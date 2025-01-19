import RPi.GPIO as GPIO
import time

LED_PIN = 4

def main():
    GPIO.setmode(GPIO.BCM)  # BCMモードでピン番号指定
    GPIO.setup(LED_PIN, GPIO.OUT)  # GPIO4を出力モードに設定
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
if __name__ == "__main__":
    main()



