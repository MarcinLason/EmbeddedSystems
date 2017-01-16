#!~/.virtualenvs/cv/bin/python

from bluetooth import *
import cv2
from picamera import PiCamera
from gpiozero import MotionSensor
import os
import sys
import time
import Queue
import threading
import logging
import datetime as dt
import wiringpi as GPIO

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
exit_opencv_flag = False
exit_program_flag = False

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


# DEFS
def initGPIO():
    GPIO.wiringPiSetupGpio()
    GPIO.pinMode(23, GPIO.INPUT)  # switching mode
    GPIO.pinMode(24, GPIO.INPUT)  # capture picture from camera
    GPIO.pinMode(25, GPIO.INPUT)  # exit from camera
    GPIO.pinMode(18, GPIO.INPUT)  # motion detector input
    GPIO.pinMode(27, GPIO.OUTPUT)  # LED indicates switching between modes
    GPIO.pinMode(22, GPIO.OUTPUT)  # LED indicates taking a photo/video
    GPIO.pullUpDnControl(23, GPIO.PUD_UP)
    GPIO.pullUpDnControl(24, GPIO.PUD_UP)
    GPIO.pullUpDnControl(25, GPIO.PUD_UP)


def initCatalogsStructure():
    if not os.path.exists('/home/pi/Desktop/Camera/Photos/'):
        os.makedirs('/home/pi/Desktop/Camera/Photos/')

    if not os.path.exists('/home/pi/Desktop/Camera/Videos/'):
        os.makedirs('/home/pi/Desktop/Camera/Videos/')

    if not os.path.exists('/home/pi/Desktop/Camera/FacesDetected/'):
        os.makedirs('/home/pi/Desktop/Camera/FacesDetected/')


def getFileName(type):
    now = dt.datetime.now()
    date = str(now.date()) + "_" + str(now.time().replace(microsecond=0))
    if (type):  # photo
        filename = "photo_" + date + '.jpg'
    else:  # video
        filename = "video_" + date + '.h264'
    return filename


def changeMode(mode):
    GPIO.digitalWrite(27, GPIO.HIGH)
    time.sleep(0.3)
    mode = (mode + 1) % 3
    if (mode == 0):
        print("Photo mode\n")
    elif (mode == 1):
        print("Video mode\n")
    elif (mode == 2):
        print("Motion Detector / Face Detecting mode\n")
    GPIO.digitalWrite(27, GPIO.LOW)
    return mode


def capturePicture():
    GPIO.digitalWrite(22, GPIO.HIGH)
    os.system('raspistill -o /home/pi/Desktop/Camera/Photos/' + getFileName(True))
    print("Just took a photo!\n")
    GPIO.digitalWrite(22, GPIO.LOW)


def captureVideo():
    GPIO.digitalWrite(22, GPIO.HIGH)
    cam = PiCamera()
    cam.start_recording('/home/pi/Desktop/Camera/Videos/' + getFileName(False))
    time.sleep(5)
    cam.stop_recording()
    print("Just recorded a video!\n")
    GPIO.digitalWrite(22, GPIO.LOW)


def tactSwitches(MODE_FLAG, tact_thread_queue):
    logging.debug('Tact thread!')
    kill_this_thread = False
    while not exit_program_flag and not kill_this_thread:
        if (GPIO.digitalRead(25) == GPIO.LOW):
            kill_this_thread = True             # kill tact switch thread; that feature
        if (GPIO.digitalRead(24) == GPIO.LOW):  # taking photo/video
            time.sleep(0.2)
            mode = tact_thread_queue.get()
            if mode == 0:                       # photo
                tact_thread_queue.put(mode)
                capturePicture()
            elif mode == 1:                     # video
                tact_thread_queue.put(mode)
                captureVideo()
        elif (GPIO.digitalRead(23) == GPIO.LOW):  # switching between modes
            time.sleep(0.2)
            mode = tact_thread_queue.get()
            if mode == 1:                         # via tact switch face detection mode is unavailable
                new_mode = 0
                print("Photo mode\n")
            elif mode == 2:
                new_mode = 2                    # via tact switch cannot exit detection mode
            else:
                new_mode = changeMode(mode)
            tact_thread_queue.put(new_mode)
    logging.debug('Tact thread stopped!')


def opencvMode():
    logging.debug('Starting openCV mode!')
    for i in reversed(range(5)):              # time to safe escape
        print("Left {0} seconds to start".format(i))
        time.sleep(1)
    print("Started detecting!")
    while not exit_opencv_flag:
        logging.debug('Working!')
        time.sleep(1)
        if(GPIO.digitalRead(18) == GPIO.HIGH):   # signal from motion detector
            # Taking photo and preparing path
            GPIO.digitalWrite(22, GPIO.HIGH)
            imageName = getFileName(True)
            fullPath = '/home/pi/Desktop/Camera/Photos/' + imageName
            os.system('raspistill -o' + fullPath)
            GPIO.digitalWrite(22, GPIO.LOW)

            # Converting image to gray version
            image = cv2.imread(fullPath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detecting faces on image and printing result
            faceCascade = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            print("Found {0} faces!".format(len(faces)))

            # Tagging faces by rectangles on image and saving tagged image
            for(x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Saving photo with faces detected to the special folder
            if (len(faces) > 0):
                cv2.imwrite('/home/pi/Desktop/Camera/FacesDetected/' + imageName, image)
    logging.debug('Exiting openCV mode!')


def cleanUp():
    # output pins set to 0
    GPIO.digitalWrite(27, GPIO.LOW)
    GPIO.digitalWrite(22, GPIO.LOW)
    # output pins set to input
    GPIO.pinMode(27, GPIO.INPUT)
    GPIO.pinMode(22, GPIO.INPUT)
    sys.exit("Good bye! :)")


initGPIO()
initCatalogsStructure()
# HELLO MESSAGES
print("Photo mode\n")

# BLUETOOTH SETUP
server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

advertise_service(server_sock, "CameraServer",
                  service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS],
                  profiles=[SERIAL_PORT_PROFILE],
                  #                   protocols = [ OBEX_UUID ]
                  )

# MAIN PROGRAM LOOP
MODE_FLAG = 0                            # [0 - photo; 1 - video; 2 - motion detector
pir = MotionSensor(18)                   # motion detector input
opencv_thread = None

tact_thread_queue = Queue.Queue()
tact_thread_queue.put(MODE_FLAG)

tact_switches_thread = threading.Thread(name='tactswitch', target=tactSwitches, args=(MODE_FLAG, tact_thread_queue))
tact_switches_thread.start()

while True:
    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        data = client_sock.recv(1024)
        if len(data) == 0:
            break
        print("received [%s]" % data)

        if data == 'switch':
            data = 'switched!'
            mode = tact_thread_queue.get()
            MODE_FLAG = changeMode(mode)
            tact_thread_queue.put(MODE_FLAG)
            if MODE_FLAG == 2:     # [OpenCV functionality]
                exit_opencv_flag = False
                opencv_thread = threading.Thread(name='opencv', target=opencvMode)
                opencv_thread.start()
                data = 'opencv_on'
            else:
                exit_opencv_flag = True
        elif data == 'exit_opencv':
            exit_opencv_flag = True # kill opencv thread
            time.sleep(1)           # wait for thread death
            opencv_thread = None
            mode = tact_thread_queue.get()
            MODE_FLAG = 0
            tact_thread_queue.put(MODE_FLAG)
            data = 'opencv_off'
        elif data == 'capture':
            data = 'capture!'
            mode = tact_thread_queue.get()
            tact_thread_queue.put(mode)
            if mode == 0:     # taking photo
                capturePicture()
            elif mode == 1:   # taking video
                captureVideo()
        elif data == 'turnOff':
            data = 'turned off!'
            exit_opencv_flag = True
            exit_program_flag = True
            client_sock.send(data)
            client_sock.close()
            server_sock.close()
            cleanUp()
        else:
            data = 'Interruption!'
        client_sock.send(data)
        print("sending [%s]" % data)

    except IOError:
        pass

    except KeyboardInterrupt:

        print("disconnected")

        client_sock.close()
        server_sock.close()
        print("all done")

        break
