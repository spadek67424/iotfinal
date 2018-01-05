
# coding: utf-8

# In[1]:

# 假設每兩個board一組，處理一側(假定8個block)
import numpy as np


# # kernel

# In[299]:

class kernel:
    def __init__(self, block_num):
        # variable
        self.carLotNum = 4
        self.lot_num = block_num
        self.mainPriority = 0 # lowest (vacant parking space)
        self.mainBias = 0 # 1 if other space have higher priority
        self.parkingPriority = block_num + 2 # parking vehicle

        # list
        self.price_list = np.array([0]*block_num)
        self.priority_list = np.array([0]*block_num)
        self.parking_list = np.array([0]*block_num)
        self.distance_list = np.array([block_num]*block_num)
        self.nearestVehicleIdx_list = np.array([idx for idx in range(block_num)])
        
    def findParkingLot(self, vehicle): # vehicle 0:scooter 1:car
        edgeDistance = 0
        vehicleDistance = 0
        edgeDistanceFromVehicle = 0
        lot_index = -1
        
        if self.parking_list.min() == 1: # full parking vehicle
#             print('none')
            lot_index = -1
        elif self.parking_list.max() == 0: # no parking vehicle
#             print('all')
            if vehicle: # car
#                 for idx in range(-1,-(self.carLotNum)-1,-1):
#                     self.parking_list[idx] = 1 # park vehicle
                lot_index = (self.lot_num-self.carLotNum)
            else: # scooter
#                 self.parking_list[0] = 1
                lot_index = 0
        
        else: # there're some parking vehicle
#             print('some')
            if vehicle: # car
                count=0
                begin = self.lot_num-1
                for idx in range(self.lot_num-1,-1,-1):
                    if self.parking_list[idx]==0:
                        count+=1
                    else:
                        count=0
                    if count==4:
#                         for in_idx in range(idx, idx-self.carLotNum, -1):
#                             self.parking_list[in_idx] = 1
                        lot_index = idx # vehicle 起始位置
            else: # scooter 
#                 self.parking_list[self.priority_list.argmin()] = 1
                lot_index = self.parking_list.argmin() # derive first min index
        
        self.mark_parking_list(lot_index, vehicle)
        self.updateLists(lot_index, vehicle)
        
        # self.broadcast_Pi_priorty()    
    
    def ParkVehicle(self,lot_index, vehicle):
        self.mark_parking_list(lot_index, vehicle)
        self.updateLists(lot_index, vehicle)
    
    def LeaveVehicle(self, lot_index, vehicle):
        self.unmark_parking_list(lot_index, vehicle)
        self.updateLists(lot_index, vehicle)
        
    ################# update main func ######################
    def updateLists(self, lot_idx, vehicle):
        if not lot_idx ==-1:
            self.update_distance_list()
            self.update_nearestVehicleIdx_list()
            self.update_priority_list()

    ################# update funcs ######################
    def mark_parking_list(self, lot_idx, vehicle):
        if vehicle ==1: # car
            for idx in range(self.carLotNum):
                self.parking_list[lot_idx+idx] = 1
                self.priority_list[lot_idx+idx] = self.parkingPriority
        else: # scooter
            self.parking_list[lot_idx] = 1
            self.priority_list[lot_idx] = self.parkingPriority
            
    def unmark_parking_list(self, lot_idx, vehicle):
        if vehicle ==1: # car
            for idx in range(self.carLotNum):
                self.parking_list[lot_idx+idx] = 0
        else: # scooter
            self.parking_list[lot_idx] = 0
            
    def update_distance_list(self):
        # According to parking list, update distance list,
        # which record distance to nearest parking vehicle
        
        if max(self.parking_list)!=0:
            distance = self.lot_num
            for idx in range(self.lot_num):
                if self.parking_list[idx] ==1: # full
                    distance = 0
                else: 
                    distance +=1
                self.distance_list[idx] = distance

            #reverse
            distance = self.lot_num
            for idx in range(self.lot_num-1,-1,-1):
                distance = (0 if self.parking_list[idx] ==1 else distance+1)
                self.distance_list[idx] = min(distance,  self.distance_list[idx])
        else: # vacant parking space
            self.parking_list = np.array([0]*block_num)
                        
        
    def update_nearestVehicleIdx_list(self):
        # According to distance_list, update nearestVehicle_list,
        # which store nearest parking vehicle's index
        
        if max(self.parking_list)!=0:
            for idx in range(self.lot_num):

                # for candidate idx
                idx_parkingLot = idx_left = idx_right = -1
                # main
                lot_side_label = ''
                distance = self.distance_list[idx]

                if distance !=0: # if parking lot vacant
                    # phase 1 : check current lot side
                    if (self.lot_num != 2*int(self.lot_num/2)) and (idx==int(self.lot_num/2)):
                        # if lot_num is odd and idx in the middle
                        lot_side_label = 'middle'
                    elif idx < self.lot_num/2 : # left
                        lot_side_label = 'left'
                    else:
                        lot_side_label = 'right'

                    # phase 2 : check nearest vehicle idx
                    idx_left = idx - distance
                    idx_right = idx + distance

                    if idx_left < 0 : # idx_left out of bound
                        idx_parkingLot = idx_right
                    elif not idx_right < self.lot_num : # idx_right out of bound
                        idx_parkingLot = idx_left
                    elif self.distance_list[idx_left] == self.distance_list[idx_right] : # both 0
                        idx_parkingLot = (idx_right if lot_side_label =='right' else idx_left)
                    else: # one side have smaller distance (equals to 0)
                        idx_parkingLot = (idx_left if self.distance_list[idx_left] ==0 else idx_right)

                    self.nearestVehicleIdx_list[idx] = idx_parkingLot
                else: # full parking lot
                    idx_parkingLot = idx

                self.nearestVehicleIdx_list[idx] = idx_parkingLot   
        else:
            self.nearestVehicleIdx_list = np.array([idx for idx in range(block_num)])
    def update_priority_list(self):       
        ## if A shortest side and urs are different, then priority = self.lot_num
        ## else priority = 2 * shortest side length 
        
        if max(self.parking_list) != 0:
            for idx in range(self.lot_num):
    #             print('idx:'+str(idx))
                lot_side_label = ''
                if self.distance_list[idx] != 0: # vacancy
                    idx_nearest = self.nearestVehicleIdx_list[idx]

                    # phase 1 : check current lot side
                    if (self.lot_num != 2*int(self.lot_num/2)) and ((idx==int(self.lot_num/2)) or (idx_nearest==int(self.lot_num/2))):
    #                     print('odd array ~')
                        # if lot_num is odd and idx in the middle
                        self.priority_list[idx] = self.lot_num + 1
                    elif idx < self.lot_num/2 : # left
    #                     print('left')
                        if idx_nearest < idx :
                            self.priority_list[idx] = (idx+1) * 2
                        elif idx_nearest < self.lot_num/2 : #left
                            self.priority_list[idx] = (idx_nearest+1) * 2
                        else:
                            self.priority_list[idx] = self.lot_num + 1
                    else: # right
    #                     print('right')
                        if idx_nearest > idx :
                            self.priority_list[idx] = (self.lot_num-idx) * 2
                        elif idx_nearest >= self.lot_num/2 : #left
                            self.priority_list[idx] = (self.lot_num-idx_nearest) * 2
                        else:
                            self.priority_list[idx] = self.lot_num + 1

                else: # reset to init value (lot_num + 2)
                    self.priority_list[idx] = self.parkingPriority
        else:
            self.priority_list = np.array([0]*block_num)
    
    def showLists(self):
        print "parking list : "
        print self.parking_list
        print "distance_list : "
        print self.distance_list 
        print "nearestVehicleIdx_list : "
        print self.nearestVehicleIdx_list
        print "priority list : "
        print self.priority_list
        print "price list : "
        print self.price_list


# # Test : condition

# In[293]:

# block_num = 11


# # In[300]:

# # condition 1 all clear
# kernel = Kernel(block_num) # 8 parking lot 

# kernel.parking_list


# # In[226]:

# # condition 2 full vehicle
# kernel = Kernel(block_num) # 8 parking lot 
# for idx in range(block_num):
#     kernel.ParkVehicle(idx,0)
    
# kernel.parking_list


# # In[301]:

# # condition 3
# kernel = Kernel(block_num) # 8 parking lot 
# kernel.ParkVehicle(lot_index=1,vehicle=0)
# kernel.ParkVehicle(lot_index=5,vehicle=1)

# kernel.parking_list


# # In[302]:

# kernel.LeaveVehicle(lot_index=1,vehicle=0)


# # # Test : findParkingLot

# # In[303]:

# kernel.showLists()

