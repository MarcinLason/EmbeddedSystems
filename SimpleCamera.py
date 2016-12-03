import os
import datetime as dt

now = dt.datetime.now()
filename = str(now.date()) + "_" + str(now.time().replace(microsecond=0)) + '.jpg'

os.system('raspistill -o /home/pi/Desktop/Camera/Photos/' + filename)
