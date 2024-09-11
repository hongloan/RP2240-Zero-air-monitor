from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)

oled = SSD1306_I2C(128,64,i2c)

msg = 'Loan'
oled.text(msg,10 ,0)
oled.text('Shahbaz',10 ,20)
oled.show()