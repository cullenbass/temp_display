import time
boot = time.ticks_ms()

SLEEP_MINUTES=1
from machine import WDT, Pin, SoftI2C, ADC, deepsleep
wdt = WDT(timeout=(1*60+30)*1000)
wdt.feed()

import aht
import network
import util

def execute():
    
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(False)
        wlan.active(True)
        wlan.connect('BoringUniFi', 'pinetree4790')
        while not wlan.isconnected():
            pass
    ip_address, netmask, gateway, dns = wlan.ifconfig()
    print("I2C setup")
    i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
    print("Preparing sensor...")
    sensor = aht.AHT2x(i2c)
    if not sensor.is_calibrated:
        print("Not calibrated, resetting sensor")
        sensor.reset()
    print("Reading sensor...")

    if sensor.is_ready:
        with open("data.csv", "a") as f:
            try:
                year,month,day,h,m,s,_ = util.get_time()
                print(f"{year}-{month:0>2d}-{day:0>2d}T{h:0>2d}:{m:0>2d}:{s:0>2d}")
                print(f"{year}-{month:0>2d}-{day:0>2d}T{h:0>2d}:{m:0>2d}:{s:0>2d}")
                adc = ADC(Pin(34))
                f.write(f"{year}-{month:0>2d}-{day:0>2d}T{h:0>2d}:{m:0>2d}:{s:0>2d},{(sensor.temperature*9/5)+32:.2f},{adc.read_uv()/1000/500}\n")
            except Exception as err:
                print(err)
    
def deep(boot):
    sleep_ms = SLEEP_MINUTES*60*1000 - time.ticks_diff(time.ticks_ms(), boot)
    if sleep_ms < 1:
        sleep_ms = 1
    print(f"Sleeping {sleep_ms}")
    deepsleep(sleep_ms)    

try:
    execute()
except Exception as err:
    print(err)
deep(boot)

