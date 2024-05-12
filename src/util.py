import urequests
import ujson

def get_time():
    try:
        req = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        if req.status_code != 200:
            print('Failed to get current time')
            print('req.text')
            return None
        dat = ujson.load(req.raw)
        return dat['unixtime'] + dat['raw_offset'] + dat['dst_offset']
    
    except Exception as e:
        print(str(e))
        return 0