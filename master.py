import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from kernel import kernel
import ast

# master board index
board_idx = 
vehicleclasslist = [[e//4 for e in range(8)]] # [0,0,0,0,1,1,1,1] 0:scooter, 1:car

def on_connect(client, userData, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("slave2master/")
    client.subscribe("broadcast/")

def on_message(client, userData, msg):
    # print("Receive from slave, index is {}".format(msg.payload))
    info = msg.payload
    info_list = info.split("|")

    if msg.topic == "slave2master/" and info_list[0]==str(board_idx-1):
        # TODO Update price when receive index from slave
        print("recieve from slave device, index is "+str(info_list[0]))
        slaveParkVehicle(info_list[1])
        time.sleep(0.05)
    elif msg.topic== "broadcast/" and info_list[0] != str(board_idx):
        # TODO Update price when receive information from broadcast
        foreignPriority = int(info_list[1])
        declareBroadcast = Kernel.update_from_broadcast(int(info_list[0]), foreignPriority)
        print("receive broadcast, index is "+str(info_list[0]))
        print('mainPriority:'+str(Kernel.mainPriority)+" | foreignPriority list: "+str(Kernel.foreignPriority_list))
        print('price list : '+str(Kernel.price_list))
        # check if best_priority broadcast is require or not
        broadcast(declareBroadcast)
        time.sleep(0.05)

def slaveParkVehicle(slave_parking_list):
    slave_parking_list = ast.literal_eval(slave_parking_list)
    vehicle = 0 # default: scooter
    change_idx = -1
    for slave_idx in range(4):
        print(slave_parking_list[slave_idx])
        if Kernel.parking_list[slave_idx] != slave_parking_list[slave_idx]:
            change_idx = slave_idx
            break
    if change_idx == -1:
        print('none of change')
    else :
        print('status changes, idx: '+str(change_idx))
        if Kernel.parking_list[change_idx]==0:
            declareBroadcast = Kernel.ParkVehicle(space_index=change_idx, vehicle=vehicle)
        else:
            declareBroadcast = Kernel.LeaveVehicle(space_index=change_idx)

        broadcast(declareBroadcast)
        
        print(Kernel.parking_list)

def broadcast(declareBroadcast):
    if declareBroadcast:
        declareMsg = str(board_idx)+'|'+ Kernel.get_broadcast_info()
        client.publish("broadcast/", declareMsg)

space_num = 8
idx = -1

# init 
Kernel = kernel(block_num=space_num)
print('kernel ready')
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.101")

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
outList = [0]*4

while True:
    out1=grovepi.digitalRead(2)
    out2=grovepi.digitalRead(3)
    out3=grovepi.digitalRead(4)
    out4=grovepi.digitalRead(5)
    if out1!=outList[0]:
        idx = 4
        if out1==0:
            grovepi.digitalWrite(6, 1)
            grovepi.digitalWrite(14,0)
            broadcast(Kernel.LeaveVehicle(space_index=idx))
            #Kernel.showStatus()
            outList[0]=0
        else:
            grovepi.digitalWrite(6,0)
            grovepi.digitalWrite(14,1)
            broadcast(Kernel.ParkVehicle(space_index=idx,vehicle=0))

            outList[0]=1
        print(Kernel.parking_list)
    if out2 != outList[1]:
        idx = 5
        if out2==0:
            grovepi.digitalWrite(7, 1)
            grovepi.digitalWrite(15,0)
            broadcast(Kernel.LeaveVehicle(space_index=idx))
            #Kernel.showStatus()
            outList[1]=0
        else:
            grovepi.digitalWrite(7,0)
            grovepi.digitalWrite(15,1)
            broadcast(Kernel.ParkVehicle(space_index=idx,vehicle=0))
            outList[1]=1
        print(Kernel.parking_list)
    if out3 != outList[2]:
        idx = 6
        if out3==0:
            grovepi.digitalWrite(8, 1)
            grovepi.digitalWrite(9,0)
            broadcast(Kernel.LeaveVehicle(space_index=idx))
            #Kernel.showStatus()
            outList[2]=0
        else:
            grovepi.digitalWrite(8,0)
            grovepi.digitalWrite(9,1)
            broadcast(Kernel.ParkVehicle(space_index=idx,vehicle=0))
            outList[2]=1
        print(Kernel.parking_list)
    if out4 != outList[3]:
        idx = 7
        if out4==0:
            grovepi.digitalWrite(16, 1)
            grovepi.digitalWrite(17,0)
            broadcast(Kernel.LeaveVehicle(space_index=idx))
            #Kernel.showStatus()
            outList[3]=0
        else:
            grovepi.digitalWrite(16,0)
            grovepi.digitalWrite(17,1)
            broadcast(Kernel.ParkVehicle(space_index=idx,vehicle=0))
            outList[3]=1
        print(Kernel.parking_list)
    time.sleep(0.1)


#time.sleep(1)
#grovepi.digitalWrite(7, 1)
#time.sleep(0.2)

