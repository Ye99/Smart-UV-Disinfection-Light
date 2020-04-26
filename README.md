# Smart-UV-Disinfection-Light
Smart controller for UV disinfection light.

# Parts list:
* ESP8266 x 1. The "brain".
* RFP30N06LE x 1. Turn on/off the UV led.
* 2n7000 x 1. Logic shifter. Distance sensor runs on 5V; ESP8266 GPIO is only 
3.3V. This shifter converts it to 5V for the sensor Trigger signal.
* 22k and 11k resistor to convert 5V echo signal to 3.3v.
* LM317 x 1. For UV Led constant current source. Credits: Lewis Loflin
http://www.bristolwatch.com/ccs/LM317.htm
* 100 Ohm Potentiometer, to adjust constant current value. 

See main.py for wiring. TODO: add wiring diragram. 
