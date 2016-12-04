import os
import time
import datetime as dt
import wiringpi as GPIO


# DEFS
def getFileName(type):
    now = dt.datetime.now()
    date = str(now.date()) + "_" + str(now.time().replace(microsecond=0))
    if(type):                               # photo
        filename = "photo_" + date + '.jpg'
    else:                                   # video
        filename = "video_" + date + '.h264'
    return filename

# SETTING UP PINS
GPIO.wiringPiSetupGpio()
GPIO.pinMode(23, GPIO.INPUT)                # switching mode
GPIO.pinMode(24, GPIO.INPUT)                # capture picture from camera
GPIO.pinMode(27, GPIO.OUTPUT)               # LED indicates switching between modes
GPIO.pinMode(22, GPIO.OUTPUT)               # LED indicates taking a photo/video
GPIO.pullUpDnControl(23, GPIO.PUD_UP)
GPIO.pullUpDnControl(24, GPIO.PUD_UP)

# MAIN PROGRAM LOOP

MODE_FLAG = True                            # if true then photo mode

while True:
    if(GPIO.digitalRead(24) == GPIO.LOW):   # taking photo/video
        time.sleep(0.2)
        if(MODE_FLAG):
            GPIO.digitalWrite(22, GPIO.HIGH)
            time.sleep(0.3)
            # os.system('raspistill -o /home/pi/Desktop/Camera/Photos/' + getFileName(True))
            print("Just took a photo!\n")
            GPIO.digitalWrite(22, GPIO.LOW)
        else:
            GPIO.digitalWrite(22, GPIO.HIGH)
            time.sleep(0.3)
            # os.system('raspivid -o /home/pi/Desktop/Camera/Video/' + getFileName(False))
            print("Just recorded a video!\n")
            GPIO.digitalWrite(22, GPIO.LOW)
    elif(GPIO.digitalRead(23) == GPIO.LOW):  # switching between modes
        time.sleep(0.2)
        GPIO.digitalWrite(27, GPIO.HIGH)
        time.sleep(0.3)
        if(MODE_FLAG):
            print("Photo mode\n")
        else:
            print("Video mode\n")
        MODE_FLAG = not MODE_FLAG
        GPIO.digitalWrite(27, GPIO.LOW)

GPIO.cleanup()

