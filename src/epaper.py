from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 14
DC_PIN          = 13
CS_PIN          = 25
BUSY_PIN        = 26

class EPD_2in9_B:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = SPI(2)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.height, self.width, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.height, self.width, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)


    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        self.send_command(0x71)
        while(self.digital_read(self.busy_pin) == 0): 
            self.send_command(0x71)
            self.delay_ms(10) 
        
    def rotate(self):
        #def bufrotate(fb, w, h, defaultcolor=1):
        rotateblack = bytearray(self.width * self.height // 8)
        rotatered = bytearray(self.width * self.height // 8)
        rotatefb = framebuf.FrameBuffer(rotateblack, self.width, self.height, framebuf.MONO_HLSB)
        rotaterb = framebuf.FrameBuffer(rotatered, self.width, self.height, framebuf.MONO_HLSB)
        for x in range(self.width):
            for y in range(self.height):
                rotatefb.pixel(x,y, self.imageblack.pixel(self.height-1-y,x))
                rotaterb.pixel(x,y, self.imagered.pixel(self.height-1-y,x))
        self.buffer_black = rotateblack
        self.buffer_red = rotatered
        
        
    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.ReadBusy()

    def init(self):
        self.reset()
        self.send_command(0x04)  
        self.ReadBusy()#waiting for the electronic paper IC to release the idle signal

        self.send_command(0x00)    #panel setting
        self.send_data(0x0f)   #LUT from OTP,128x296
        self.send_data(0x89)    #Temperature sensor, boost and other related timing settings

        self.send_command(0x61)    #resolution setting
        self.send_data (0x80)  
        self.send_data (0x01)  
        self.send_data (0x28)

        self.send_command(0X50)    #VCOM AND DATA INTERVAL SETTING
        self.send_data(0x77)   #WBmode:VBDF 17|D7 VBDW 97 VBDB 57
                            # WBRmode:VBDF F7 VBDW 77 VBDB 37  VBDR B7
        return 0       
        
    def display(self):
        self.rotate()
        self.send_command(0x10)
        self.send_data1(self.buffer_black)
                
        self.send_command(0x13)
        self.send_data1(self.buffer_red)   

        self.TurnOnDisplay()
    
    def Clear(self, colorblack, colorred):
        self.send_command(0x10)
        self.send_data1([colorblack] * self.height * int(self.width / 8))
                
        self.send_command(0x13)
        self.send_data1([colorred] * self.height * int(self.width / 8))
        
        self.TurnOnDisplay()
    def Clear_Async(self, colorblack, colorred):
        self.send_command(0x10)
        self.send_data1([colorblack] * self.height * int(self.width / 8))
                
        self.send_command(0x13)
        self.send_data1([colorred] * self.height * int(self.width / 8))
        self.send_command(0x12)
        
    def sleep(self):
        self.send_command(0X02) # power off
        self.ReadBusy()
        self.send_command(0X07) # deep sleep
        self.send_data(0xA5)
        
        self.delay_ms(2000)
        self.module_exit()
