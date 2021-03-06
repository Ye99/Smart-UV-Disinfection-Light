from time import sleep_ms, ticks_ms, ticks_diff

from machine import Pin, ADC, reset
from micropython import const

from hcsr04 import HCSR04
from umqtt.simple import MQTTClient

_led_light_on_milliseconds = const(30000)
_led_light_current_to_voltage_resistor_value = const(47)

# Wiring:
# D7 UV light switch. High == on.
uv_light = Pin(13, Pin.OUT)


def turn_on_uv_light() -> None:
    uv_light.on()


def turn_off_uv_light() -> None:
    uv_light.off()


turn_off_uv_light()

# A0 UV light current (47 Ohm resister converts current to voltage) measurement.
uv_light_voltage = ADC(0)  # value 0, 1024 corresponding to 0. 3.3V


def map_adc_reading_to_voltage(value, left_min, left_max, right_min, right_max) -> float:
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


def measure_uv_light_current() -> float:
    current_ma = map_adc_reading_to_voltage(uv_light_voltage.read(),
                                            _ADC_reading_low_range,
                                            _ADC__reading_high_range,
                                            _ADC_voltage_low_range,
                                            _ADC_voltage_high_range) / \
                 _led_light_current_to_voltage_resistor_value * 1000
    # print('UV light current is {} mA'.format(current_ma))
    return current_ma


_last_x_distance_values = []
_track_distance_value_number = const(8)


def compute_average(values_list) -> float:
    assert len(values_list) > 0, "doesn't make sense to compute empty list average"
    # print('values_list length is {}'.format(len(values_list)))
    if len(values_list) > 0:
        average = sum(values_list) / len(values_list)
        return average
    else:
        return 0


# Sometime the ultrasonic sensor returns readings much shorter than true value. Track the last x values and
# use their average to filter out such noise.
def update_distance_average(new_measure) -> float:
    if len(_last_x_distance_values) > _track_distance_value_number:
        _last_x_distance_values.pop(0)

    _last_x_distance_values.append(new_measure)
    return compute_average(_last_x_distance_values)


# Only call this method called when WiFi is connected.
# See https://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html#configuration-of-the-wifi
# ESP8266/32 persist WiFi configuration during power-off, and will reconnect automatically.
def publish_message(message) -> None:  # message is in binary format
    print('Publish message: {0}'.format(message))
    try:
        c = MQTTClient(client_id="smart_uv_light_umqtt_client",  # if username/pwd wrong, this will throw Exception
                       server="192.168.1.194",
                       user=b"mosquitto",
                       password=b"mosquitto",
                       ssl=False)
        if 0 == c.connect():  # 0 is success.
            c.publish(b"smart_uv_light_status_topic", message)
            c.disconnect()
        else:
            print('Connect to MQTT server failed. ')
    except OSError as exception:
        # When machine is just booted, WiFi hasn't been connected yet. Immediately invoke MQTT will throw error.
        # Instead of tracking startup grace period, just keep code simple by catching and log the error.
        print('publish_message encountered error {}'.format(exception))


last_reset_tick = ticks_ms()
_reset_interval_milliseconds = const(60 * 1000 * 30 )  # 30 minutes


def periodically_reset() -> None:
    tick_ms_elapsed = ticks_diff(ticks_ms(), last_reset_tick)
    # message = 'tick_ms elapsed {}'.format(tick_ms_elapsed)
    # publish_message(message)
    # print(message)

    if tick_ms_elapsed > _reset_interval_milliseconds:
        # free is in boot so it's available to REPL, for convenience. Import it to make this dependency explicit?
        publish_message('Reset. Current memory usage is {}'.format(free()))  # Also works as heartbeat.
        sleep_ms(2000)
        reset()
        #  Don't need to record last_reset_tick here. Because after reset, code will do it.


# ESP32 Devkit print Dxx, the xx is pin number used below.
# ESP8266 map Dxx to GPIO number https://randomnerdtutorials.com/esp8266-pinout-reference-gpios/
# D5 Trigger (reversed logic, low -> high because of the MOSFET driver in front of distance sensor.
# HCSR04 library needs to be modified)
# D6 Echo
sensor = HCSR04(trigger_pin=14, echo_pin=12)

start_ticks = 0

_loop_sleep_ms = const(6)
_led_on_distance_cm = const(73)  # 29 inch

# For testing average function.
# import urandom

while True:
    try:
        distance_reading = sensor.distance_cm()
        # distance_reading = urandom.getrandbits(8)
        # print('The last distance reading is {} cm.'.format(distance_reading))
        if distance_reading <= 2:
            # It can give negative readings. Hardware bug or library bug?
            # print('Drop value below the Ultrasonic lower range.')
            continue

        average_distance = update_distance_average(distance_reading)
        # print('Current average distance is {} cm.'.format(average_distance))

        if average_distance < _led_on_distance_cm and uv_light.value() == 0:
            start_ticks = ticks_ms()
            turn_on_uv_light()
            publish_message('Turn light on. Average distance {}. '
                            'Light current is {} mA. '.format(average_distance, measure_uv_light_current()))
        if 1 == uv_light.value() and ticks_diff(ticks_ms(), start_ticks) > _led_light_on_milliseconds:
            # publish_message('Before turning light off. Current is {} mA.'.format(measure_uv_light_current()))
            turn_off_uv_light()
            publish_message('Light is off. Current is {} mA.'.format(measure_uv_light_current()))

        measure_uv_light_current()
        periodically_reset()
        sleep_ms(_loop_sleep_ms)
    except OSError as ex:
        error_message = 'ERROR: {}'.format(ex)
        # If function, invoked from here, raises exception, the loop can terminate.
        publish_message(error_message)
        print(error_message)
