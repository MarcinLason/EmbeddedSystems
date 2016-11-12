CC=gcc
CFLAGS=-Wall
WPI=-lwiringPi

all: tact_switch

tact_switch: tact_switch.c
	$(CC) $(CFLAGS) $(WPI) -o $@ $^

clean:
	rm -f *.a *.o tact_switch
