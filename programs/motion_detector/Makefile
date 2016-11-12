CC=gcc
CFLAGS=-Wall
WPI=-lwiringPi

all: motion_detector

motion_detector: motion_detector.c
	$(CC) $(CFLAGS) $(WPI) -o $@ $^

clean:
	rm -f *.a *.o motion_detector
