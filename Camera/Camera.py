import os
import time
import datetime as dt
import wiringpi as GPIO
from picamera import PiCamera
from gpiozero import MotionSensor


# DEFS
def getFileName(type):
    now = dt.datetime.now()
    date = str(now.date()) + "_" + str(now.time().replace(microsecond=0))
    if(type):                               # photo
        filename = "photo_" + date + '.jpg'
    else:                                   # video
        filename = "video_" + date + '.h264'
    return filename

def changeMode(mode):
    GPIO.digitalWrite(27, GPIO.HIGH)
    time.sleep(0.3)
    mode = (mode + 1) % 3
    if(mode == 0):
        print("Photo mode\n")
    elif(mode == 1):
        print("Video mode\n")
    elif(mode == 2):
        print("Motion Detector Video mode\n")
    GPIO.digitalWrite(27, GPIO.LOW)
    return mode

# SETTING UP PINS
GPIO.wiringPiSetupGpio()
GPIO.pinMode(23, GPIO.INPUT)                # switching mode
GPIO.pinMode(24, GPIO.INPUT)                # capture picture from camera
GPIO.pinMode(18, GPIO.INPUT)                # motion detector input
pir = MotionSensor(18)                      # motion detector input
GPIO.pinMode(27, GPIO.OUTPUT)               # LED indicates switching between modes
GPIO.pinMode(22, GPIO.OUTPUT)               # LED indicates taking a photo/video
GPIO.pullUpDnControl(23, GPIO.PUD_UP)
GPIO.pullUpDnControl(24, GPIO.PUD_UP)

# HELLO MESSAGES
print("Photo mode\n")

# MAIN PROGRAM LOOP

MODE_FLAG = 0                            # [0 - photo; 1 - video; 2 - motion detector

while True:
    if(GPIO.digitalRead(24) == GPIO.LOW and MODE_FLAG == 0):   # taking photo/video
        time.sleep(0.2)
        GPIO.digitalWrite(22, GPIO.HIGH)
        time.sleep(0.3)
        os.system('raspistill -o /home/pi/Desktop/Camera/Photos/' + getFileName(True))
        print("Just took a photo!\n")
        GPIO.digitalWrite(22, GPIO.LOW)
    elif(GPIO.digitalRead(24) == GPIO.LOW and MODE_FLAG == 1):
        time.sleep(0.2)
        GPIO.digitalWrite(22, GPIO.HIGH)
        time.sleep(0.3)
        cam = PiCamera()
        cam.start_recording('/home/pi/Desktop/Camera/Videos/' + getFileName(False))
        while(GPIO.digitalRead(24) == GPIO.LOW):
            pass
        cam.stop_recording()
        print("Just recorded a video!\n")
        GPIO.digitalWrite(22, GPIO.LOW)
    elif(GPIO.digitalRead(24) == GPIO.LOW):        # modify - it appears in photo mode too
        print("You are in 'motion detector video mode'")
    elif(GPIO.digitalRead(18) and MODE_FLAG == 2):
        GPIO.digitalWrite(22, GPIO.HIGH)
        time.sleep(0.3)
        cam = PiCamera()
        cam.start_recording('/home/pi/Desktop/Camera/Videos/' + getFileName(False))
        pir.wait_for_no_motion()
        cam.stop_recording()
        print("Just recorded a video after motion detected!\n")
        GPIO.digitalWrite(22, GPIO.LOW)
    elif(GPIO.digitalRead(23) == GPIO.LOW):  # switching between modes
        time.sleep(0.2)
        MODE_FLAG = changeMode(MODE_FLAG)

GPIO.cleanup()
