from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import sht31
import time

# For changing the text size of SSD1306
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_15, ubuntu_mono_20

# I2C buses set up

# I2C0 for the sensors
i2cSensor = I2C(0, sda=Pin(0), scl=Pin(1), freq =400000)
sensor1 = sht31.SHT31(i2cSensor, addr=0x44)
sensor2 = sht31.SHT31(i2cSensor, addr=0x45)

# I2C1 for the oled screen
i2cOled = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
oled = SSD1306_I2C(128,64,i2cOled)

# Define the font size
write15 = Write(oled, ubuntu_mono_15)
write20 = Write(oled, ubuntu_mono_20)

msg = 'Indoor Outdoor'
while True:
    t1,humi1 = sensor1.get_temp_humi()
    t2,humi2 = sensor2.get_temp_humi()
    write15.text(msg,10 ,0)
    write15.text(str("{:.2f}".format(t1)),0 ,20)
    write15.text(str("{:.2f}".format(humi1)),0 ,40)
    write15.text(str("{:.2f}".format(t2)),70 ,20)
    write15.text(str("{:.2f}".format(humi2)),70 ,40)
    oled.show()
    time.sleep(2)
    oled.fill(0) #erase entire screen
    

