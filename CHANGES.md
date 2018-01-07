## [Pricing stratgy and vehicle spaces control](#)
> Jan 08, 2018
1. change price startegy : 
    - there's only two price following scooter parking space, 10 or 20, which depend on the priority. Only one or few parking space have 10 dollars price, other are set to 20 becuase of lower priority.
    - If parking vehicle is car. Price is set to 40. (and 80 dollar when parking space is in the middle of the parking lot)
2. add **car_parking_space_request** function to master.py : when 4 sides of car space are parked, the **master** with last parked space will send request to next **master** (with board_index). next **master** will merge scooter space to car one if there have enough parking space, or the **master** will pass the request to next **master** again.

## [Link from raspberryPi to kernel, add some show function](#).
> Jan 07, 2018

1. add functions to **kernel.py** :
	- _**parkingVerification(space_idx, vehicle)**_ : check if the parking request is legal or not. Print error message and then reject if the request is illegal.
	- _**show_priceInfo**_ : print each parking space's price whether it has been parked or not
	- _**show_parkInfo(space_idx, vehicle)**_ : print parking info. when parking request comes and accepted . (inside func:_**ParkVehicle**_)
	- _**show_leaveInfo(space_idx, income)**_ : print leaving info. when vehicle leaves . (inside func:_**unmark_parkingleavetime_list**_)

2. add **simulation.ipynb** to simulate whether algorithm is robust in multi-kernel (parking lots) situation

3. rename **trygrove.py** as **master.py** or **slave.py**, depends on board task
4. delete **udpdevice_mag_strip.py**, **turnallrgboff** and **WukongStandardLibrary.xml**, because we dont apply **[Wukong](http://iox.ntu.edu.tw/research/projectinfo/wukong)** at all.


> Jan 06, 2018

1. modify **udpdevice_mag_strip.py** :
	- pull _**kernel callee**_ out from _Magnetic WuClass_ and packed as a function for multiple sensor trigger
2. add _int_ and _list_ variables to **kernel.py** :
	- _**timeInterval**_ : total price = price * timeInterval
	- _**parkingstarttime_list**_ : store parking start time for each parking space (second base)
	- _**vehicleLabel_list**_ : init no vehicle(-1), store car(1) or scooter(0) for each praking space
3. add functions to **kernel.py** :
	- _**mark_vehicleLabel_list(space_idx, vehicle)**_ : 
	- _**unmark_vehicleLabel_list(space_idx)**_ :
	- _**mark_parkingstarttime_list**_ :
	- _**unmark_parkingleavetime_list(space_idx)**_ :
	- _**update_totalIncome_(starttime, leavetime, price)**_ :
4. modify functions in **kernel.py** :
	- _**LeaveVehicle**_ :
	- _**unmark_praking_list**_ :
5. create kernel directory and move **kernel.py** into it
6. create **simulation.ipnb** for large parking spaces simulation

> Jan 05, 2018

1. add **kernel.py** : parking algorithm class
2. modify **udpdevice_mag_strip.py** :
	- modify _**update**_ function, add kernel callee and 0.05 sec latency foreach status-changes