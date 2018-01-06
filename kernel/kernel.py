
# coding: utf-8

# In[118]:

import numpy as np
import time

class kernel:
    def __init__(self, block_num=8, # theres <block_num> parking space a side (kernel)
                 basePrice=40, # at least <basePrice> dollar a timeInterval
                 carspaceNum=4, # a car space equals to <carspaceNum> scooters space
                 timeInterval=60 # 1 min
                ):
        
        # variable
        self.totalIncome = 0
        self.mainPriority = 0 # lowest (vacant parking space)
        self.mainBias = 0 # 1 if other space have higher priority
        self.foreignPriority = 0 # record foreign Priority
        # self.foreign_vehicle_num = 0

        # custom variable
        self.timeInterval = timeInterval
        self.carspaceNum = carspaceNum
        self.space_num = block_num
        self.basePrice = basePrice
        self.parkingPriority = block_num + 2 # parking vehicle

        # list
        self.price_list = np.array([0]*block_num)
        self.priority_list = np.array([0]*block_num)
        self.parking_list = np.array([0]*block_num)
        self.distance_list = np.array([block_num]*block_num)
        self.accPrice_list = np.array([0]*block_num)
        self.nearestVehicleIdx_list = np.array([idx for idx in range(block_num)])
        self.parkingstarttime_list = np.array([0]*block_num)
        self.vehicleLabel_list = np.array([-1]*block_num)
        
        # process
        self.update_price_list()
        self.update_mainBias()
        
    def findParkingspace(self, vehicle): # vehicle 0:scooter 1:car
        edgeDistance = 0
        vehicleDistance = 0
        edgeDistanceFromVehicle = 0
        space_index = -1
        
        if self.parking_list.min() == 1: # full parking vehicle
#             print('none')
            space_index = -1
        elif self.parking_list.max() == 0: # no parking vehicle
#             print('all')
            if vehicle: # car
#                 for idx in range(-1,-(self.carspaceNum)-1,-1):
#                     self.parking_list[idx] = 1 # park vehicle
                space_index = (self.space_num-self.carspaceNum)
            else: # scooter
#                 self.parking_list[0] = 1
                space_index = 0
        
        else: # there're some parking vehicle
#             print('some')
            if vehicle: # car
                count=0
                begin = self.space_num-1
                for idx in range(self.space_num-1,-1,-1):
                    if self.parking_list[idx]==0:
                        count+=1
                    else:
                        count=0
                    if count==4:
#                         for in_idx in range(idx, idx-self.carspaceNum, -1):
#                             self.parking_list[in_idx] = 1
                        space_index = idx # vehicle 起始位置
            else: # scooter 
#                 self.parking_list[self.priority_list.argmin()] = 1
                space_index = self.parking_list.argmin() # derive first min index
        
        self.mark_parking_list(space_index, vehicle)
        self.updateLists(space_index, vehicle)
        
        # self.broadcast_Pi_priorty()    
    
    def ParkVehicle(self,space_index, vehicle):
        self.mark_parkingstarttime_list(space_index, vehicle)
        self.mark_parking_list(space_index, vehicle)
        self.mark_vehicleLabel_list(space_index, vehicle)
        self.updateLists(space_index)
    
    def LeaveVehicle(self, space_index):        
        self.unmark_parkingleavetime_list(space_index)
        self.unmark_parking_list(space_index)
        self.unmark_vehicleLabel_list(space_index)
        self.updateLists(space_index)
        
    ################# update main func ######################
    def updateLists(self, space_idx):
        if not space_idx ==-1:
            self.update_distance_list()
            self.update_nearestVehicleIdx_list()
            self.update_priority_list()
            self.update_mainPriority()
            self.update_price_list()

    ################## mark func. #######################
    def mark_parking_list(self, space_idx, vehicle):
        if vehicle ==1: # car
            for idx in range(self.carspaceNum):
                self.parking_list[space_idx+idx] = 1
                self.priority_list[space_idx+idx] = self.parkingPriority
        else: # scooter
            self.parking_list[space_idx] = 1
            self.priority_list[space_idx] = self.parkingPriority
            
    def unmark_parking_list(self, space_idx):
        vehicle = self.vehicleLabel_list[space_idx]
        
        if vehicle ==1: # car
            for idx in range(self.carspaceNum):
                self.parking_list[space_idx+idx] = 0
        else: # scooter
            self.parking_list[space_idx] = 0
            
    def mark_vehicleLabel_list(self, space_idx, vehicle):
        if vehicle ==1:
            for idx in range(self.carspaceNum):
                self.vehicleLabel_list[space_idx+idx] = 1 # car
        else:
            self.vehicleLabel_list[space_idx] = 0 # scooter
                
    def unmark_vehicleLabel_list(self, space_idx):
        vehicle = self.vehicleLabel_list[space_idx]
        if vehicle ==1:
            for idx in range(self.carspaceNum):
                self.vehicleLabel_list[space_idx+idx] = -1
        else:
            self.vehicleLabel_list[space_idx] = -1
    
    def mark_parkingstarttime_list(self, space_idx, vehicle):
        parkingtime = time.time()
        if vehicle==1: # car
            for idx in range(self.carspaceNum):
                self.parkingstarttime_list[space_idx+idx] = parkingtime
        else: # scooter
            self.parkingstarttime_list[space_idx] = parkingtime
            
    def unmark_parkingleavetime_list(self, space_idx):
        leavetime = time.time()
        starttime = self.parkingstarttime_list[space_idx]
        price = self.price_list[space_idx]
        vehicle = self.vehicleLabel_list[space_idx]
        
        # get income updated
        self.update_totalIncome(starttime, leavetime, price)

        if vehicle==1:
            for idx in range(self.carspaceNum):
                self.parkingstarttime_list[space_idx+idx]=0
        else:
            self.parkingstarttime_list[space_idx] = 0
    

    ################# update func. #######################
    def update_distance_list(self):
        # According to parking list, update distance list,
        # which record distance to nearest parking vehicle
        
        if max(self.parking_list)!=0:
            distance = self.space_num
            for idx in range(self.space_num):
                if self.parking_list[idx] ==1: # full
                    distance = 0
                else: 
                    distance +=1
                self.distance_list[idx] = distance

            #reverse
            distance = self.space_num
            for idx in range(self.space_num-1,-1,-1):
                distance = (0 if self.parking_list[idx] ==1 else distance+1)
                self.distance_list[idx] = min(distance,  self.distance_list[idx])
        else: # vacant parking space
            self.parking_list = np.array([0]*self.space_num)
                        
        
    def update_nearestVehicleIdx_list(self):
        # According to distance_list, update nearestVehicle_list,
        # which store nearest parking vehicle's index
        
        if max(self.parking_list)!=0:
            for idx in range(self.space_num):

                # for candidate idx
                idx_parkingspace = idx_left = idx_right = -1
                # main
                space_side_label = ''
                distance = self.distance_list[idx]

                if distance !=0: # if parking space vacant
                    # phase 1 : check current space side
                    if (self.space_num != 2*int(self.space_num/2)) and (idx==int(self.space_num/2)):
                        # if space_num is odd and idx in the middle
                        space_side_label = 'middle'
                    elif idx < self.space_num/2 : # left
                        space_side_label = 'left'
                    else:
                        space_side_label = 'right'

                    # phase 2 : check nearest vehicle idx
                    idx_left = idx - distance
                    idx_right = idx + distance

                    if idx_left < 0 : # idx_left out of bound
                        idx_parkingspace = idx_right
                    elif not idx_right < self.space_num : # idx_right out of bound
                        idx_parkingspace = idx_left
                    elif self.distance_list[idx_left] == self.distance_list[idx_right] : # both 0
                        idx_parkingspace = (idx_right if space_side_label =='right' else idx_left)
                    else: # one side have smaller distance (equals to 0)
                        idx_parkingspace = (idx_left if self.distance_list[idx_left] ==0 else idx_right)

                    self.nearestVehicleIdx_list[idx] = idx_parkingspace
                else: # full parking space
                    idx_parkingspace = idx

                self.nearestVehicleIdx_list[idx] = idx_parkingspace   
        else:
            self.nearestVehicleIdx_list = np.array([idx for idx in range(self.space_num)])
    
    def update_priority_list(self):       
        ## if A shortest side and urs are different, then priority = self.space_num
        ## else priority = 2 * shortest side length 
        
        if max(self.parking_list) != 0:
            for idx in range(self.space_num):
    #             print('idx:'+str(idx))
                space_side_label = ''
                if self.distance_list[idx] != 0: # vacancy
                    idx_nearest = self.nearestVehicleIdx_list[idx]

                    # phase 1 : check current space side
                    if (self.space_num != 2*int(self.space_num/2)) and ((idx==int(self.space_num/2)) or (idx_nearest==int(self.space_num/2))):
    #                     print('odd array ~')
                        # if space_num is odd and idx in the middle
                        self.priority_list[idx] = self.space_num + 1
                    elif idx < self.space_num/2 : # left
    #                     print('left')
                        if idx_nearest < idx :
                            self.priority_list[idx] = (idx+1) * 2
                        elif idx_nearest < self.space_num/2 : #left
                            self.priority_list[idx] = (idx_nearest+1) * 2
                        else:
                            self.priority_list[idx] = self.space_num + 1
                    else: # right
    #                     print('right')
                        if idx_nearest > idx :
                            self.priority_list[idx] = (self.space_num-idx) * 2
                        elif idx_nearest >= self.space_num/2 : #left
                            self.priority_list[idx] = (self.space_num-idx_nearest) * 2
                        else:
                            self.priority_list[idx] = self.space_num + 1

                else: # reset to init value (space_num + 2)
                    self.priority_list[idx] = self.parkingPriority
        else:
            self.priority_list = np.array([0]*self.space_num)
        self.update_mainPriority()
    
    def update_price_list(self):
        bias = self.mainBias
        
        # update parking space prices where space is vacant and priority has been changed
        for idx in range(self.space_num):
            if self.parking_list[idx] == 0 : # vacancy
                # update price
                self.price_list[idx] = self.basePrice + self.priority_list[idx] + bias - self.mainPriority
        
    #####################################################

    def update_from_broadcast(self, foreignPriority, foreign_vehicle_num): 
        # vehicle_num = sum(self.parking_list):
        if self.mainPriority < self.foreignPriority :# or (self.foreignPriority==self.mainPriority and vehicle_num > self.foreign_vehicle_num):
            self.mainBias = 1
            self.foreignPriority = foreignPriority
        else:
            self.mainBias = 0
            self.foreignPriority = self.mainPriority
        self.update_price_list()

    def update_mainBias(self):
        if self.mainPriority < self.foreignPriority:
            mainBias = 1
        else:
            mainBias = 0

    def update_mainPriority(self):
        self.mainPriority = min(self.priority_list)
        self.update_mainBias()
    
    def update_totalIncome(self, starttime, leavetime, price):
        times = int((leavetime - starttime)/self.timeInterval) + 1
        self.totalIncome += (times * price)
        
    #####################################################
    def showLists(self):
        
        # python2

        # print "parking list : "
        # print self.parking_list
        # print "distance_list : "
        # print self.distance_list 
        # print "nearestVehicleIdx_list : "
        # print self.nearestVehicleIdx_list
        # print "priority list : "
        # print self.priority_list
        # print "price list : "
        # print self.price_list
        # print "vehicleLabel list" 
        # print self.vehicleLabel_list 
        # print "parkingstarttime list" 
        # print [int(time.time()-t) if t>0 else 0 for t in self.parkingstarttime_list]

        print("parking list : ")
        print(self.parking_list)
        print("distance_list : ")
        print(self.distance_list )
        print("nearestVehicleIdx_list : ")
        print(self.nearestVehicleIdx_list)
        print("priority list : ")
        print(self.priority_list)
        print("price list : ")
        print(self.price_list)
        print("vehicleLabel list")
        print(self.vehicleLabel_list)
        print("parkingstarttime list")
        print([int(time.time()-t) if t>0 else 0 for t in self.parkingstarttime_list])
    
    def showStatus(self):
        
        # python 2
        
        # print "mainPriority"
        # print self.mainPriority
        # print "mainBias"
        # print self.mainBias
        # print "totalIncome"
        # print self.totalIncome

        print("mainPriority")
        print(self.mainPriority)
        print("mainBias")
        print(self.mainBias)
        print("totalIncome")
        print(self.totalIncome)
