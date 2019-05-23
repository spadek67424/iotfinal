> Jan 06, 2018

1. modify **udpdevice_mag_strip.py** :
	- pull _kernel callee_ out from _Magnetic WuClass_ and packed as a function for multiple sensor trigger
2. add _int_ and _list_ variables to **kernel.py** :
	- _timeInterval_ : total price = price * timeInterval
	- _parkingstarttime_list_ : store parking start time for each parking space (second base)
	- _vehicleLabel_list_ : init no vehicle(-1), store car(1) or scooter(0) for each praking space
3. add functions to **kernel.py** :
	- _mark_vehicleLabel_list(space_idx, vehicle)_ : 
	- _unmark_vehicleLabel_list(space_idx)_ :
	- _mark_parkingstarttime_list_ :
	- _unmark_parkingleavetime_list(space_idx)_ :
	- _update_totalIncome_(starttime, leavetime, price)_ :
4. modify functions in **kernel.py** :
	- _LeaveVehicle_ :
	- _unmark_praking_list_ :
5. create kernel directory and move **kernel.py** into it
6. create **simulation.ipnb** for large parking spaces simulation

> Jan 05, 2018

1. add **kernel.py** : parking algorithm class
2. modify **udpdevice_mag_strip.py** :
	- modify _update_ function, add kernel callee and 0.05 sec latency foreach status-changes