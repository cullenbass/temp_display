import urequests
import ujson
import struct
from time import gmtime
from machine import SoftI2C, Pin, RTC
import aht

def get_time(connected):
    rtc = RTC()
    if connected:
        try:
            req = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')
            if req.status_code != 200:
                print('Failed to get current time')
                print(req.text)
                return None
            dat = ujson.load(req.raw)
            raw_time = dat['unixtime'] + dat['raw_offset'] + dat['dst_offset']
            dow = dat['day_of_week']
            offset = int((dat['raw_offset'] + dat['dst_offset']) /60/60)
            year,month,day,h,m,s,_,_ = gmtime(raw_time)
            year = year - 30
            rtc.init((year, month, day, dow, h, m, s, 0))
            return year, month, day, h, m, s
        
        except Exception as e:
            print(str(e))
            return 0
    else:
        year, month, day, wd, h, m, s, us = rtc.datetime()
        return year, month, day, h, m, s,

def get_temp():
    i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
    sensor = aht.AHT2x(i2c)
    if not sensor.is_calibrated:
        print("Not calibrated, resetting sensor")
        sensor.reset()
    while not sensor.is_ready:
        pass
    return ((sensor.temperature*9/5)+32)

def get_its():
    rtc = RTC()
    dat = rtc.memory()
    if len(dat) < 1:
        print('failed to get memory')
        return 0
    print(f'Got from memory: {int(dat[0])}')
    return int(dat[0])

def get_stored_temp():
    rtc = RTC()
    dat = rtc.memory()
    if len(dat) > 0:
        return struct.unpack("f", dat[1:])[0]
    return 0.0

def store_data(its, temp):
    rtc = RTC()
    dat = bytes([its]) + struct.pack("f", temp)
    rtc.memory(dat)
    print(f'stored dat: {rtc.memory()}')
