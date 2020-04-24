from hcsr04 import HCSR04

# ESP32 Devkit print Dxx, the xx is pin number used below.
# echo_pin needs
sensor = HCSR04(trigger_pin=13, echo_pin=12)

try:
    distance = sensor.distance_cm()
    print('Distance:', distance, 'cm')
except OSError as ex:
    print('ERROR getting distance:', ex)