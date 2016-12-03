#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <wiringPi.h>
#include <stdbool.h>

char * getFilename(int isVideo) {
	time_t t = time(NULL);
	struct tm tm = *localtime(&t);

	char * filename = (char*)malloc(32 * sizeof(char));
	char * year = (char*)malloc(4 * sizeof(char));
	char * month = (char*)malloc(2 * sizeof(char));
	char * day = (char*)malloc(2 * sizeof(char));
	char * hour = (char*)malloc(2 * sizeof(char));
	char * minute = (char*)malloc(2 * sizeof(char));
	char * second = (char*)malloc(2 * sizeof(char));

	sprintf(year, "%d", tm.tm_year + 1900);
	sprintf(month, "%d", tm.tm_mon + 1);
	sprintf(day, "%d", tm.tm_mday);
	sprintf(hour, "%d", tm.tm_hour);
	sprintf(minute, "%d", tm.tm_min);
	sprintf(second, "%d", tm.tm_sec);

	if(isVideo == 0){
		strcpy (filename, "photo_");
	}
	else {
		strcpy (filename, "video_");
	}

	strcat(filename, year);
	strcat(filename, "-");
	strcat(filename, month);
	strcat(filename, "-");
	strcat(filename, day);
	strcat(filename, "-");
	strcat(filename, hour);
	strcat(filename, ":");
	strcat(filename, minute);
	strcat(filename, ":");
	strcat(filename, second);
	if(isVideo == 0){
		strcat(filename, ".jpg");
	}
	else {
		strcat(filename, ".h264");
	}
	return filename;
}




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


    //After acceptation for this piece of code I will move it to another file.
    char * filename = (char*)malloc(30 * sizeof(char));
    filename = getFilename(0);

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
		printf("Just recorded a video!\n");
	    }
	} else if(digitalRead(23) == LOW) {
	    delay(200);
	    printf("switch me to another mode, set up flag or something\n");
	    MODE_FLAG = !MODE_FLAG;
	}
    }
    

    return 0;
}
