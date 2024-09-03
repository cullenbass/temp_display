import urequests
import ujson
from time import gmtime
from machine import SoftI2C, Pin
import aht

def get_time():
    try:
        req = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        if req.status_code != 200:
            print('Failed to get current time')
            print('req.text')
            return None
        dat = ujson.load(req.raw)
        raw_time = dat['unixtime'] + dat['raw_offset'] + dat['dst_offset']
        offset = int((dat['raw_offset'] + dat['dst_offset']) /60/60)
        year,month,day,h,m,s,_,_ = gmtime(raw_time)
        year = year - 30
        return year, month, day, h, m, s, offset
    
    except Exception as e:
        print(str(e))
        return 0
    
def get_temp():
    i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
    sensor = aht.AHT2x(i2c)
    if not sensor.is_calibrated:
        print("Not calibrated, resetting sensor")
        sensor.reset()
    while not sensor.is_ready:
        pass
    return ((sensor.temperature*9/5)+32)