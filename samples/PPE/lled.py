import RPi.GPIO as GPIO
import time
import sys

LED_PIN_G = 22 #緑
LED_PIN_Y = 27 #黄
LED_PIN_R = 17 #赤

def main(mode):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(LED_PIN_G, GPIO.OUT)
    GPIO.setup(LED_PIN_Y, GPIO.OUT)
    GPIO.setup(LED_PIN_R, GPIO.OUT)

    if mode == "G":
        GPIO.output(LED_PIN_G, GPIO.HIGH)
        GPIO.output(LED_PIN_Y, GPIO.LOW)
        GPIO.output(LED_PIN_R, GPIO.LOW)
    elif mode == "Y":
        GPIO.output(LED_PIN_G, GPIO.LOW)
        GPIO.output(LED_PIN_Y, GPIO.HIGH)
        GPIO.output(LED_PIN_R, GPIO.LOW)
    elif mode == "R":
        GPIO.output(LED_PIN_G, GPIO.LOW)
        GPIO.output(LED_PIN_Y, GPIO.LOW)
        GPIO.output(LED_PIN_R, GPIO.HIGH)
    else:
        GPIO.cleanup()
        return

if __name__ == "__main__":
    main(sys.argv[1])



