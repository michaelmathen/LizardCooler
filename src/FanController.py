import RPi.GPIO as GPIO
from time import sleep
import os
import time
import subprocess
from multiprocessing import Process

setTemp=79

thermal_device_1 = "/sys/bus/w1/devices/28-000007c66992/w1_slave"
thermal_device_2 = "/sys/bus/w1/devices/28-000007c6f484/w1_slave"

Motor1A = 16
Motor1B = 18
Motor1E = 22

Motor2A = 37
Motor2B = 35
Motor2E = 33

startFan = lambda mE: GPIO.output(mE,GPIO.HIGH)
stopFan = lambda mE: GPIO.output(mE,GPIO.LOW)

def setupFan(mA, mB, mE):
    GPIO.setup(mA,GPIO.OUT)
    GPIO.setup(mB,GPIO.OUT)
    GPIO.setup(mE,GPIO.OUT)
    GPIO.output(mA,GPIO.HIGH)
    GPIO.output(mB,GPIO.LOW)
    stopFan(mE)


def setup():
    GPIO.setmode(GPIO.BOARD)
    setupFan(Motor1A, Motor1B, Motor1E)
    setupFan(Motor2A, Motor2B, Motor2E)
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')


def cleanup():
    GPIO.cleanup()


def try_read(device_file):
    """
    Replace this with async reading.
    """
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 

def parseFile(lines):
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f
    else:
        return None

def adjust_temperature(mA, mB, mE, thermal_file, setTemp):
    setupFan(mA, mB, mE)
    while True:
        file_string = try_read(thermal_file)
        if file_string is None:
            print("File is not being read properly")
            startFan(mE)
        temperature_f = parseFile(file_string)
        if temperature_f > setTemp + 1:
            startFan(mE)
        elif temperature_f < setTemp - 1:
            stopFan(mE)
        sleep(10)
	


if __name__ == "__main__":
    setup()
    p1 = Process(target=adjust_temperature, args=(Motor1A, Motor1B, Motor1E,
                                                  thermal_device_1, setTemp))
    p2 = Process(target=adjust_temperature, args=(Motor2A, Motor2B, Motor2E,
                                                  thermal_device_2, setTemp))
    p1.start()
    p2.start()
