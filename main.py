from hcsr04 import HCSR04
from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin, ADC
from micropython import const

_led_light_on_milliseconds = const(30000)
_led_light_current_to_voltage_resiter_value = const(47)

# Wiring:
# D7 UV light switch. High == on.
uv_light = Pin(13, Pin.OUT)


def turn_on_UV_light() -> None:
    uv_light.on()


def turn_off_UV_light() -> None:
    uv_light.off()


turn_off_UV_light()

# D5 Trigger (reversed logic, low -> high because of the MOSFET driver in front of distance sensor.
# HCSR04 library needs to be modified)
# D6 Echo


# A0 UV light current (47 Ohm resister converts current to voltage) measurement.
uv_light_voltage = ADC(0)  # value 0, 1024 corresponding to 0. 3.3V


def map_ADC_reading_to_voltage(value, left_min, left_max, right_min, right_max) -> float:
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)


_ADC_reading_low_range = const(0)
_ADC__reading_high_range = const(1024)
_ADC_voltage_low_range = const(0)
_ADC_voltage_high_range = 3.3

def measure_UV_light_current() -> float:
    current_ma = map_ADC_reading_to_voltage(uv_light_voltage.read(),
                                            _ADC_reading_low_range,
                                            _ADC__reading_high_range,
                                            _ADC_voltage_low_range,
                                            _ADC_voltage_high_range) / \
                 _led_light_current_to_voltage_resiter_value * 1000
    print('UV light current is {} mA'.format(current_ma))
    return current_ma


# ESP32 Devkit print Dxx, the xx is pin number used below.
# ESP8266 map Dxx to GPIO number https://randomnerdtutorials.com/esp8266-pinout-reference-gpios/
sensor = HCSR04(trigger_pin=14, echo_pin=12)

start_ticks = 0

_loop_sleep_ms = const(200)
_led_on_distance_cm = const(40)

while True:
    try:
        distance = sensor.distance_cm()
        print('Distance:', distance, 'cm')

        if distance < _led_on_distance_cm and uv_light.value() == 0:
            start_ticks = ticks_ms()
            turn_on_UV_light()
        if ticks_diff(ticks_ms(), start_ticks) > _led_light_on_milliseconds:
            turn_off_UV_light()

        measure_UV_light_current()

        sleep_ms(_loop_sleep_ms)
    except OSError as ex:
        print('ERROR getting distance:', ex)
