from udpwkpf import WuClass, Device
import sys
from udpwkpf_io_interface import *
from twisted.internet import reactor
from raspledstrip.ledstrip import *
import time
from Kernel import kernel

Magnetic_Pin_1 = 2
Magnetic_Pin_2 = 3
Magnetic_Pin_3 = 4
Magnetic_Pin_4 = 5

stirp_num = 4

if __name__ == "__main__":
    Kernel = kernel(block_num = strip_num)
    strip_status_list = [False] * 4

    class Magnetic_Sensor(WuClass):

        def __init__(self, pin):
            WuClass.__init__(self)
            self.loadClass('magnetic')
            self.magnetic_gpio = pin_mode(pin, PIN_TYPE_DIGITAL, PIN_MODE_INPUT)
            
            print "Megnetic Sensor init success"

        def update(self,obj,pID=None,val=None):
            try:
                on_off = digital_read(self.magnetic_gpio)
                obj.setProperty(0, on_off)

                # print "Magnetic sensor value: ", on_off
                # event trigger
                if strip_status_list[pID] != val:
                    if val:
                        Kernel.ParkVehicle(pID, 0) # scooter
                        
                    else:
                        Kernel.LeaveVehicle(pID, 0) # scooter
                    strip_status_list[pID] = val
                    Kernel.showLists()
                time.sleep(0.05)

            except IOError:
                print ("Error")

    class LED_Strip(WuClass):
        def __init__(self):
            WuClass.__init__(self)
            self.loadClass("LED_strip")
            self.strip = LEDStrip(4)
            #TODO Set color to green
            self.strip.fill(Color(0, 255, 0, 0.5), start=0, end=3)
            self.strip.update()
            print "LED Strip init success"

        def update(self, obj, pID=None, val=None):
            try:
                if pID == 0:
                    if val == True:
                        self.strip.fill(Color(255, 0, 0, 0.5), start=0, end=0)
                        self.strip.update()
                        time.sleep(0.1)
                    else:
                        self.strip.fill(Color(0, 255, 0, 0.5), start=0, end=0)
                        self.strip.update()
                        time.sleep(0.1)
                elif pID == 1:
                    if val == True:
                        self.strip.fill(Color(255, 0, 0, 0.5), start=1, end=1)
                        self.strip.update()
                        time.sleep(0.1)
                    else:
                        self.strip.fill(Color(0, 255, 0, 0.5), start=1, end=1)
                        self.strip.update()
                        time.sleep(0.1)
                elif pID == 2:
                    if val == True:
                        self.strip.fill(Color(255, 0, 0, 0.5), start=2, end=2)
                        self.strip.update()
                        time.sleep(0.1)
                    else:
                        self.strip.fill(Color(0, 255, 0, 0.5), start=2, end=2)
                        self.strip.update()
                        time.sleep(0.1)
                elif pID == 3:
                    if val == True:
                        self.strip.fill(Color(255, 0, 0, 0.5), start=3, end=3)
                        self.strip.update()
                        time.sleep(0.1)
                    else:
                        self.strip.fill(Color(0, 255, 0, 0.5), start=3, end=3)
                        self.strip.update()
                        time.sleep(0.1)
            except:
                print "Error"

    class MyDevice(Device):
        def __init__(self,addr,localaddr):
            Device.__init__(self,addr,localaddr)

        def init(self):
            m1 = Magnetic_Sensor(2)
            self.addClass(m1, 0)
            self.obj_magnetic_sensor_1 = self.addObject(m1.ID)

            m2 = Magnetic_Sensor(3)
            self.addClass(m2, 0)
            self.obj_magnetic_sensor_2 = self.addObject(m2.ID)

            m3 = Magnetic_Sensor(4)
            self.addClass(m3, 0)
            self.obj_magnetic_sensor_3 = self.addObject(m3.ID)

            m4 = Magnetic_Sensor(5)
            self.addClass(m4, 0)
            self.obj_magnetic_sensor_4 = self.addObject(m4.ID)

            m5 = LED_Strip()
            self.addClass(m5, 0)
            self.obj_led_strip = self.addObject(m5.ID)

    if len(sys.argv) <= 2:
        print 'python %s <gip> <dip>:<port>' % sys.argv[0]
        print '      <gip>: IP addrees of gateway'
        print '      <dip>: IP address of Python device'
        print '      <port>: An unique port number'
        print ' ex. python %s 192.168.4.7 127.0.0.1:3000' % sys.argv[0]
        sys.exit(-1)

    d = MyDevice(sys.argv[1],sys.argv[2])
    reactor.run()
