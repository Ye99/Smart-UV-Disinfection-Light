#!/bin/bash
curl -o .esp8266firmware.bin http://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin
esptool.py --port /dev/ttyUSB0 erase_flash && esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 .esp8266firmware.bin && rshell -p /dev/ttyUSB0 --buffer-size=30