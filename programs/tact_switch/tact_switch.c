#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <wiringPi.h>
#include <stdbool.h>

int main() {

    printf("Lets's start!");
    wiringPiSetupGpio();
    pinMode(21, INPUT);
    pullUpDnControl(21, PUD_UP);
    
    printf("What else?\n");

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    //char *date = strcat((char*)(tm.tm_year + 1900), (char*)(tm.tm_mon +1));
    //printf("%s\n", date);
    printf("now: %d-%d-%d %d:%d:%d\n", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
    
    while(true) {
	if(digitalRead(21) == LOW) {
	    //system("raspistill -o /home/pi/Desktop/Camera/Photos/photo.jpg");
	    delay(200);
	    printf("Just took a photo!\n");
	}
    }
    

    return 0;
}
