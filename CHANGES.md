> Jan 06, 2018

1. modify **udpdevice_mag_strip.py** :
	- pull _kernel callee_ out from _Magnetic WuClass_ and packed as a function for multiple sensor trigger

> Jan 05, 2018

1. add **kernel.py** : parking algorithm class
2. modify **udpdevice_mag_strip.py** :
	- modify _update_ function, add kernel callee and 0.05 sec latency foreach status-changes