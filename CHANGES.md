> Jan 06, 2018

- modify udpdevice_mag_strip.py :
	1. pull kernel callee out from Magnetic WuClass and packed as a function for multiple sensor trigger

> Jan 05, 2018

- add kernel.py : parking algorithm class
- modify udpdevice_mag_strip.py :
	1. modify update function, add kernel callee and 0.05 sec latency foreach status-changes