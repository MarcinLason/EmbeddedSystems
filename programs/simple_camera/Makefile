CC=gcc
CFLAGS=-Wall
WPI=-lwiringPi

all: simple_camera

simple_camera: simple_camera.c
	$(CC) $(CFLAGS) $(WPI) -o $@ $^

clean:
	rm -f *.a *.o simple_camera
