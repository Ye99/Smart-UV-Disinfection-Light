from hcsr04 import HCSR04
from time import sleep_ms

# ESP32 Devkit print Dxx, the xx is pin number used below.
# echo_pin needs
sensor = HCSR04(trigger_pin=13, echo_pin=12)

while True:
    try:
        distance = sensor.distance_cm()
        print('Distance:', distance, 'cm')
        sleep_ms(500)
    except OSError as ex:
        print('ERROR getting distance:', ex)

