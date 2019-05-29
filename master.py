import time
import grovepi
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from kernel import kernel
import ast
import numpy as np



# master board index
board_idx = 

def on_connect(client, userData, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("slave2master/") # inform master that space has been changed
    client.subscribe("master2slave/") # inform slave that space class has been changed
    client.subscribe("broadcast/") # basic broadcast to all other master when parking lot status change
    client.subscribe("carSpaceRequest/") # when all car spaces has been parked, broadcast merge request
    client.subscribe("scooterSpaceRequest/") # when all scooter spaces has been parked, broadcast split request


def on_message(client, userData, msg):
    # print("Receive from slave, index is {}".format(msg.payload))
    info = msg.payload
    info_list = info.split("|")

    if msg.topic == "slave2master/" and info_list[0]==str(board_idx-1):
        # TODO Update price when receive index from slave
        #print("recieve from slave device, index is "+str(info_list[0]))
        slaveParkVehicle(info_list[1])
        # time.sleep(0.05)

    elif msg.topic== "broadcast/" and info_list[0] != str(board_idx):
        # TODO Update price when receive information from broadcast
        foreignPriority = int(info_list[1])
        declareBroadcast = Kernel.update_from_broadcast(int(info_list[0]), foreignPriority)
        # print("receive broadcast, index is "+str(info_list[0]))
        # print('mainPriority:'+str(Kernel.mainPriority)+" | foreignPriority list: "+str(Kernel.foreignPriority_list))
        print_price_list()
        # print("broadcast : mainPriority : "+str(Kernel.mainPriority))
        # print('priority list : ' + str(Kernel.priority_list))
        # check if best_priority broadcast is require or not
        broadcast(declareBroadcast)
        # time.sleep(0.05)

    elif msg.topic == "carSpaceRequest/" and info_list[0]==str((board_idx-2)%8): # previous board_idx
        if not checkCarSpaceExistAndVacant():
            if check_mergeScooterSpace(): # sucessful split a space
                print("find 4 scooter parking space for a car space")
                pass
            else: # cant find one
                declareMsg = str(board_idx)+'|'
                client.publish("carSpaceRequest/", declareMsg)
                print("pass the request to next master board")


    # elif msg.topic == "scooterSpaceRequest/" and info_list[0]==str((board_idx+2)%4): # previous board_idx
    #     if not checkCarSpaceExistAndVacant():
    #         if check_splitCarSpace(): # sucessful split a space
    #             print("find 4 scooter parking space for a car space")
    #             pass
    #         else: # cant find one
    #             client.publish("carSpaceRequest/", str(board_idx))
    #             print("pass the request to next master board")


def checkCarSpaceExistAndVacant():
    result = False
    checkList = np.array(vehicleclasslist).copy()
    if not max(checkList)==0: # exist car space
        car_idx = -1
        for l_idx, label in enumerate(vehicleclasslist):
            if label==1:
                car_idx = l_idx
                break
        if Kernel.parking_list[car_idx]!=1: # vacant
            result = True
    return result


def print_price_list():
    price_list = Kernel.price_list.copy()
    times = -1
    begin_idx = -1
    for i, price in enumerate(price_list):
        if vehicleclasslist[i] ==1:
            if i ==0 or i ==4:
                times = 1
            else:
                times = 2
            begin_idx = i
            break
    if min(np.array(vehicleclasslist))==1:
        # all car space
        price_list = [50,50,50,50,50,50,50,50]
    else:
        for i in range(4):
            price_list[begin_idx+i] = 50 * times

    print('price list : '+str(price_list))

def slaveParkVehicle(slave_parking_list):
    slave_parking_list = ast.literal_eval(slave_parking_list)
    change_idx = -1
    for slave_idx in range(4):
        # print(slave_parking_list[slave_idx])
        if Kernel.parking_list[slave_idx] != slave_parking_list[slave_idx]:
            change_idx = slave_idx
            break


    vehicle = vehicleclasslist[change_idx]
    change_idx = real_idx(change_idx, vehicle)
    if change_idx == -1:
        print('none of change')
    else :
        # print('status changes, idx: '+str(change_idx))
        if Kernel.parking_list[change_idx]==0:
            broadcast(Kernel.ParkVehicle(space_index=change_idx, vehicle=vehicle), change_idx, vehicle, 1)
            changeLight(1, change_idx, vehicle)
        else:
            broadcast(Kernel.LeaveVehicle(space_index=change_idx), change_idx, vehicle, 0)
            changeLight(0, change_idx, vehicle)

        print("parking list : "+str(Kernel.parking_list))

def changeLight(mode, real_idx, vehicle):
    # send boardcast carSpaceRequest
    if vehicle:
        for idx in range(real_idx):
            led_control(idx, mode)

        if mode==1: # park
            client.publish("carSpaceRequest/", str(board_idx))
            # print("publish carSpaceRequest .. "+str(board_idx))
        # else: # leave
        #     client.publish("scooterSpaceRequest", str(board_idx))

def broadcast(declareBroadcast, real_idx=None, vehicle=None, mode=None):
    print_price_list()
    if declareBroadcast:
        change_mainBias()
        declareMsg = str(board_idx)+'|'+ Kernel.get_broadcast_info()
        # print("broadcast : mainPriority : "+str(Kernel.mainPriority))
        # print('priority list : ' + str(Kernel.priority_list))
        client.publish("broadcast/", declareMsg)

    # if slave need change several LED mode
    if real_idx!=None and real_idx<4 and vehicle==1:
        # print('need to inform slave ')
        slave_change_list = [0]*4
        for idx in range(real_idx, 4):
            slave_change_list[idx]=1
        declareMsg = str(board_idx)+'|'+ str(mode) + '|' + str(slave_change_list)
        client.publish("master2slave/", declareMsg)
    time.sleep(0.1)
    print("==================================================")

def change_mainBias():
    init = True # if scooter spacefull
    for i in range(8):
        if Kernel.vehicleclasslist[i]==0 and Kernel.parking_list[i]==0: # exist some vacant scooter space
            init = False
    if init:
        # print('scooter full')
        Kernel.mainPriority = 1

def check_splitCarSpace():
    count = 0
    splitSpace = False
    car_idx = -1
    for idx, element in enumerate(vehicleclasslist):
        count = (count+1 if element==1 and Kernel.parking_list[idx]==0 else 0)
        if count == 4 :
            car_idx = idx-3
            splitSpace =True
    if splitSpace:
        for idx in range(4):
            vehicleclasslist[idx+car_idx] = 1 # trans to car space

    return splitSpace

def check_mergeScooterSpace():
    count = 0
    mergeSpace = False
    first_scooter_idx = -1
    for idx, element in enumerate(vehicleclasslist):
        count = (count+1 if element==0 and Kernel.parking_list[idx]==0 else 0)# scooter space and it stiil be vacant
        if count == 4 :
            first_scooter_idx = idx-3
            mergeSpace = True
    if mergeSpace:
        for idx in range(4):
            vehicleclasslist[idx+first_scooter_idx] = 1
            Kernel.vehicleclasslist[idx+first_scooter_idx] =1

    return mergeSpace

def real_idx(idx, vehicle):
    tmp_idx = idx
    if vehicle==1: # if car , find best
        for minus in range(4):
            tmp_idx = idx - minus
            if vehicleclasslist[tmp_idx] == 0:
                tmp_idx += 1
                break

    return tmp_idx

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

space_num = 8

# init 
Kernel = kernel(block_num=space_num)
print('kernel ready')
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
outList = [0]*4
vehicleclasslist = [e//4 for e in range(8)] # [0,0,0,0,1,1,1,1] 0:scooter, 1:car
idx = -1
vehicle = -1

while True:
    out1=grovepi.digitalRead(2)
    out2=grovepi.digitalRead(3)
    out3=grovepi.digitalRead(4)
    out4=grovepi.digitalRead(5)
    if out1!=outList[0]:
        idx = 4
        vehicle=vehicleclasslist[idx]
        if out1==0:
            grovepi.digitalWrite(6, 1)
            grovepi.digitalWrite(14,0)
            broadcast(Kernel.LeaveVehicle(space_index=real_idx(idx, vehicle)), real_idx(idx, vehicle), vehicle, 0)
            changeLight(0, real_idx(idx, vehicle), vehicle)
            outList[0]=0
        else:
            grovepi.digitalWrite(6,0)
            grovepi.digitalWrite(14,1)
            broadcast(Kernel.ParkVehicle(space_index=real_idx(idx, vehicle), vehicle=vehicle), real_idx(idx, vehicle), vehicle, 1)
            changeLight(1, real_idx(idx, vehicle), vehicle)
            outList[0]=1
        print(Kernel.parking_list)
    if out2 != outList[1]:
        idx = 5
        vehicle=vehicleclasslist[idx]
        if out2==0:
            grovepi.digitalWrite(7, 1)
            grovepi.digitalWrite(15,0)
            broadcast(Kernel.LeaveVehicle(space_index=real_idx(idx, vehicle)), real_idx(idx, vehicle), vehicle, 0)
            changeLight(0, real_idx(idx, vehicle), vehicle)            
            outList[1]=0
        else:
            grovepi.digitalWrite(7,0)
            grovepi.digitalWrite(15,1)
            broadcast(Kernel.ParkVehicle(space_index=real_idx(idx, vehicle), vehicle=vehicle), real_idx(idx, vehicle), vehicle, 1)
            changeLight(1, real_idx(idx, vehicle), vehicle)

            outList[1]=1
        print(Kernel.parking_list)
    if out3 != outList[2]:
        idx = 6
        vehicle=vehicleclasslist[idx]
        if out3==0:
            grovepi.digitalWrite(8, 1)
            grovepi.digitalWrite(9,0)
            broadcast(Kernel.LeaveVehicle(space_index=real_idx(idx, vehicle)), real_idx(idx, vehicle), vehicle, 0)
            changeLight(0, real_idx(idx, vehicle), vehicle)            
            outList[2]=0
        else:
            grovepi.digitalWrite(8,0)
            grovepi.digitalWrite(9,1)
            broadcast(Kernel.ParkVehicle(space_index=real_idx(idx, vehicle), vehicle=vehicle), real_idx(idx, vehicle), vehicle, 1)
            changeLight(1, real_idx(idx, vehicle), vehicle)
            
            outList[2]=1
        print(Kernel.parking_list)
    if out4 != outList[3]:
        idx = 7
        vehicle = vehicleclasslist[idx]
        if out4==0:
            grovepi.digitalWrite(16, 1)
            grovepi.digitalWrite(17,0)
            broadcast(Kernel.LeaveVehicle(space_index=real_idx(idx, vehicle)), real_idx(idx, vehicle), vehicle, 0)
            changeLight(0, real_idx(idx, vehicle), vehicle)
            
            outList[3]=0
        else:
            grovepi.digitalWrite(16,0)
            grovepi.digitalWrite(17,1)
            broadcast(Kernel.ParkVehicle(space_index=real_idx(idx, vehicle), vehicle=vehicle), real_idx(idx, vehicle), vehicle, 1)
            changeLight(1, real_idx(idx, vehicle), vehicle)
            
            outList[3]=1
        print(Kernel.parking_list)
    time.sleep(0.1)





#time.sleep(1)
#grovepi.digitalWrite(7, 1)
#time.sleep(0.2)

