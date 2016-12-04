import os
import time
import datetime as dt
import wiringpi as GPIO
# from picamera import PiCamera


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
GPIO.pinMode(18, GPIO.INPUT)                # motion detector input
GPIO.pinMode(27, GPIO.OUTPUT)               # LED indicates switching between modes
GPIO.pinMode(22, GPIO.OUTPUT)               # LED indicates taking a photo/video
GPIO.pullUpDnControl(23, GPIO.PUD_UP)
GPIO.pullUpDnControl(24, GPIO.PUD_UP)

# HELLO MESSAGES
print("Photo mode\n")

# MAIN PROGRAM LOOP

MODE_FLAG = 0                            # [0 - photo; 1 - video; 2 - motion detector

while True:
    if(GPIO.digitalRead(24) == GPIO.LOW):   # taking photo/video
        time.sleep(0.2)
        if(MODE_FLAG == 0):
            GPIO.digitalWrite(22, GPIO.HIGH)
            time.sleep(0.3)
            os.system('raspistill -o /home/pi/Desktop/Camera/Photos/' + getFileName(True))
            print("Just took a photo!\n")
            GPIO.digitalWrite(22, GPIO.LOW)
        elif(MODE_FLAG == 1):
            GPIO.digitalWrite(22, GPIO.HIGH)
            time.sleep(0.3)
            os.system('raspivid -o /home/pi/Desktop/Camera/Videos/' + getFileName(False))
            print("Just recorded a video!\n")
            GPIO.digitalWrite(22, GPIO.LOW)
        else:
            print("You are in 'motion detector video mode'")
    elif(GPIO.digitalRead(18) and MODE_FLAG == 2):
        GPIO.digitalWrite(22, GPIO.HIGH)
        time.sleep(0.3)
        os.system('raspivid -o /home/pi/Desktop/Camera/Videos/' + getFileName(False))
        print("Just recorded a video after motion detected!\n")
        GPIO.digitalWrite(22, GPIO.LOW)

    elif(GPIO.digitalRead(23) == GPIO.LOW):  # switching between modes
        time.sleep(0.2)
        GPIO.digitalWrite(27, GPIO.HIGH)
        time.sleep(0.3)
        MODE_FLAG = (MODE_FLAG + 1) % 3
        if(MODE_FLAG == 0):
            print("Photo mode\n")
        elif(MODE_FLAG == 1):
            print("Video mode\n")
        elif(MODE_FLAG == 2):
            print("Motion Detector Video mode\n")
        GPIO.digitalWrite(27, GPIO.LOW)
    '''else:            records with speed up, interesting...
        cam = PiCamera()    wider angle of recording? check it out
        cam.start_recording(getFileName(False))
        time.sleep(6)
        cam.stop_recording()'''

GPIO.cleanup()
