#include<stdlib.h>
#include<stdio.h>
#include<wiringPi.h>
#include<stdbool.h>

int main() {

    printf("Lets's start!");
    wiringPiSetupGpio();
    pinMode(14, INPUT);
    pullUpDnControl(14, PUD_DOWN);
    
    while(true) {
	if(digitalRead(14) == HIGH) {
	    delay(2);
	    //system("raspivid -o /home/pi/Desktop/Camera/Videos/video.h264");
	    printf("Just made a video!");
	}
    }
    

    return 0;
}
