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

grovepi.digitalWrite(6, 1)
grovepi.digitalWrite(7, 1)
grovepi.digitalWrite(8, 1)
grovepi.digitalWrite(9, 1)
grovepi.digitalWrite(14, 1)
grovepi.digitalWrite(15, 1)
grovepi.digitalWrite(16, 1)
grovepi.digitalWrite(17, 1)