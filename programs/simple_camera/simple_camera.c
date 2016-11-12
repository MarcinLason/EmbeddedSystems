#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <wiringPi.h>
#include <stdbool.h>

int main() {

    //-------SETTING UP PINS----
    wiringPiSetupGpio();
    pinMode(23, INPUT);			//switching mode
    pinMode(24, INPUT);			//capture picture from camera
    pullUpDnControl(23, PUD_UP);
    pullUpDnControl(24, PUD_UP);
    

    //-------SETTING DATE TO DIFFERENTIATE NAME OF FILE----

    //should be set in while loop!!!!!
    //here just leave declarations

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    //char *date = strcat((char*)(tm.tm_year + 1900), (char*)(tm.tm_mon +1));
    //printf("%s\n", date);
    printf("now: %d-%d-%d %d:%d:%d\n", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);

    //-------MAIN PROGRAM LOOP

    bool MODE_FLAG = true;		//if true then photo mode
    
    while(true) {
	if(digitalRead(24) == LOW) {
	    delay(200);
	    if(MODE_FLAG) {
	        //system("raspistill -o /home/pi/Desktop/Camera/Photos/photo.jpg");
	        printf("Just took a photo!\n");
	    } else {
		//system("raspivid -o /home/pi/Desktop/Camera/Videos/video.h264");
		printf("Just recorded a video!");
	    }
	} else if(digitalRead(23) == LOW) {
	    delay(200);
	    printf("switch me to another mode, set up flag or something");
	    MODE_FLAG = !MODE_FLAG;
	}
    }
    

    return 0;
}
