import time
import grovepi
import RPi.GPIO as GPIO
grovepi.pinMode(6,"OUTPUT")
grovepi.pinMode(7,"OUTPUT")
grovepi.pinMode(8,"OUTPUT")
grovepi.pinMode(9,"OUTPUT")

grovepi.pinMode(14,"OUTPUT")
grovepi.pinMode(15,"OUTPUT")
grovepi.pinMode(16,"OUTPUT")
grovepi.pinMode(17,"OUTPUT")

grovepi.pinMode(2,"INPUT")
grovepi.pinMode(3,"INPUT")
grovepi.pinMode(4,"INPUT")
grovepi.pinMode(5,"INPUT")
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(12,GPIO.OUT)
#GPIO.output(12,0)
#grovepi.pinMode(7,"OUTPUT")
#grovepi.pinMode(button,"INPUT")

#out=grovepi.digitalRead(button)
#if out==0:
#   data=(data+1)%2
#while True:
out1=0
out2=0
out3=0
out4=0
while True:
    out1=grovepi.digitalRead(2)
    out2=grovepi.digitalRead(3)
    out3=grovepi.digitalRead(4)
    out4=grovepi.digitalRead(5)
    if out1==1:
        grovepi.digitalWrite(6, 1)
        grovepi.digitalWrite(14,0)
    else:
        grovepi.digitalWrite(6,0)
        grovepi.digitalWrite(14,1)
    if out2==1:
        grovepi.digitalWrite(7, 1)
        grovepi.digitalWrite(15,0)
    else:
        grovepi.digitalWrite(7,0)
        grovepi.digitalWrite(15,1)
    if out3==1:
        grovepi.digitalWrite(8, 1)
        grovepi.digitalWrite(9,0)
    else:
        grovepi.digitalWrite(8,0)
        grovepi.digitalWrite(9,1)
    if out4==1:
        grovepi.digitalWrite(16, 1)
        grovepi.digitalWrite(17,0)
    else:
        grovepi.digitalWrite(16,0)
        grovepi.digitalWrite(17,1)

#time.sleep(1)
#grovepi.digitalWrite(7, 1)
#time.sleep(0.2)

