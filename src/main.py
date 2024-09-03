import time
boot = time.ticks_ms()

weather_lat = 34.1419
weather_long = -84.2025
SLEEP_MINUTES = 1 

from machine import WDT, deepsleep
wdt = WDT(timeout=(1*60+30)*1000)
wdt.feed()
from epaper import EPD_2in9_B
import network
import weather_api
import util

def execute():
    screen = EPD_2in9_B()
    screen.init()
    #screen.Clear_Async(0xff,0xff)

    # set up wifi
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(False)
        wlan.active(True)
        wlan.connect('BoringUniFi', 'pinetree4790')
        while not wlan.isconnected():
            pass
    ip_address, netmask, gateway, dns = wlan.ifconfig()

    outdoor = weather_api.get_current_temp(weather_lat, weather_long)
    screen.imageblack.fill(0xff)
    screen.imagered.fill(0xff)
    # 37 characters long
    screen.imageblack.text("IP address: " + ip_address, 0, 2, 0x00)
    screen.imageblack.text("Gateway: " + gateway, 0, 12, 0x00)
    screen.imageblack.text(f'Outdoor Temperature:', 0, 50, 0x00)
    screen.imagered.text(f'{outdoor} F', 21*8, 50, 0x00)
    indoor = util.get_temp() 
    year,month,day,h,m,s,_ = util.get_time()
    screen.imageblack.text(f'Indoor Temperature:', 0, 60, 0x00)
    screen.imagered.text(f'{indoor:.1f} F', 21*8, 60, 0x00)
    screen.imageblack.text(f'Last Update: {month:02d}/{day:02d} {h:02d}:{m:02d}:{s:02d}', 0, 70, 0x00)
    screen.ReadBusy()
    screen.display()
    screen.sleep()

def deep(boot):
    sleep_ms = SLEEP_MINUTES*60*1000 - time.ticks_diff(time.ticks_ms(), boot)
    if sleep_ms < 1:
        sleep_ms = 1
    deepsleep(sleep_ms)

if __name__ == '__main__':
    try:
        execute()

    except Exception as err:
        screen = EPD_2in9_B()
        screen.init()
        screen.imageblack.fill(0xff)
        screen.imagered.fill(0xff)
        line = -1
        for x in range(len(str(err))):
            if x%35 == 0:
                line = line + 1
            screen.imageblack.text(str(err)[x], (x%35)*8, 2+line*10, 0x00)
        screen.display()

    deep(boot)

