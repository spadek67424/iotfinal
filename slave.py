import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import ast

# slave board index
board_idx = 

def on_connect(client, userData, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("master2slave/") # inform slave that space class has been changed


def on_message(client, userData, msg):
    # print("Receive from slave, index is {}".format(msg.payload))
    info = msg.payload
    info_list = info.split("|")
    # print('receive from master')
    # print(info_list)

    if msg.topic == "master2slave/" and info_list[0]==str(board_idx+1):
        # TODO Update price when receive index from slave
        print("recieve from master device, index is "+str(info_list[0]))
        mode = int(info_list[1]) # 0:leave, 1:parked
        idx_list = ast.literal_eval(info_list[2])
        turnLight(mode=mode , idx_list=idx_list)

def turnLight(mode, idx_list):
    for idx in range(4):
        if idx_list[idx]: # need change
            led_control(idx, mode)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.104")

client.loop_start()

grovepi.pinMode(6,"OUTPUT") #led 1 R
grovepi.pinMode(7,"OUTPUT") #led 2 R
grovepi.pinMode(8,"OUTPUT") #led 3 R
grovepi.pinMode(9,"OUTPUT") #led 3 G

grovepi.pinMode(14,"OUTPUT") #led 1 G
grovepi.pinMode(15,"OUTPUT") #led 2 G
grovepi.pinMode(16,"OUTPUT") #led 4 R
grovepi.pinMode(17,"OUTPUT") #led 4 G

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
outList=[0]*4

def initial_rgb():
    #TODO All LED turn ON
    grovepi.digitalWrite(6,1)
    grovepi.digitalWrite(14,0)
    grovepi.digitalWrite(7,1)
    grovepi.digitalWrite(15,0)
    grovepi.digitalWrite(8,1)
    grovepi.digitalWrite(9,0)
    grovepi.digitalWrite(16,1)
    grovepi.digitalWrite(17,0)

def led_control(index, r_or_g):
    assert index<4,"index must < 4"
    if index==0:
        if r_or_g==0:#green
            grovepi.digitalWrite(6,1)
            grovepi.digitalWrite(14,0)
        else:
            grovepi.digitalWrite(6,0)
            grovepi.digitalWrite(14,1)

    elif index==1:
        if r_or_g==0:#green
            grovepi.digitalWrite(7,1)
            grovepi.digitalWrite(15,0)
        else:
            grovepi.digitalWrite(7,0)
            grovepi.digitalWrite(15,1)
    elif index==2:
	if r_or_g==0:#green
            grovepi.digitalWrite(8,1)
            grovepi.digitalWrite(9,0)
        else:
            grovepi.digitalWrite(8,0)
            grovepi.digitalWrite(9,1)
    elif index==3:
	if r_or_g==0:#green
            grovepi.digitalWrite(16,1)
            grovepi.digitalWrite(17,0)
        else:
            grovepi.digitalWrite(16,0)
            grovepi.digitalWrite(17,1)
initial_rgb()


print('slave board ready')
while True:
    out1=grovepi.digitalRead(2)
    out2=grovepi.digitalRead(3)
    out3=grovepi.digitalRead(4)
    out4=grovepi.digitalRead(5)
    if out1!=outList[0]:
        if out1==0:
            led_control(0, out1)
            outList[0]=0
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
        else:
            led_control(0,out1)
            outList[0]=1
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
            
    if out2!=outList[1]:
        if out2==0:
            led_control(1,out2)
            outList[1]=0
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
        else:
            led_control(1,out2)
            outList[1]=1
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
           
    if out3!=outList[2]:
        if out3==0:
            led_control(2,out3)
            outList[2]=0
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
        else:
            led_control(2,out3)
            outList[2]=1
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
            
    if out4!=outList[3]:
        if out4==0:
            led_control(3,out4)
            outList[3]=0
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
        else:
            led_control(3,out4)
            outList[3]=1
            client.publish("slave2master/", str(board_idx)+"|"+str(outList))
    time.sleep(0.1)
#time.sleep(1)
#grovepi.digitalWrite(7, 1)
#time.sleep(0.2)

