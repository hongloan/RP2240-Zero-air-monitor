# MIT License

# Copyright (c) 2025 Thuy Hong Loan Le

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import time
from pms5003st import PMS5003
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import machine
import ili9225
import myfont20sb


import adafruit_sgp30
import sht31



from time import sleep

#original name
#LCDSgp30Pms5003st.py



# Initialize I2C0 bus
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# # Oled screen and sht31 is connected to I2C0
# 
# sensor1 = sht31.SHT31(i2c0, addr=0x44)

# Initialize I2C1 bus
i2c1 = I2C(1, sda=Pin(14), scl=Pin(15), freq =100000)

# SGP30 is connected to I2C1
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c1)

print("""pms5003_test.py - Continously print all data values.
""")
first_column = 0
second_column = 80

# Configure the PMS5003 for Enviro+
pms5003 = PMS5003(
    uart=machine.UART(1, tx=machine.Pin(8), rx=machine.Pin(9), baudrate=9600),
    pin_enable=machine.Pin(3),
    pin_reset=machine.Pin(10),
    mode="active"
)

# Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()

# Wait 15 seconds for the SGP30 to properly initialize
print("Waiting 15 seconds for SGP30 initialization.")
time.sleep(15)

# Retrieve previously stored baselines, if any (helps the compensation algorithm).
has_baseline = False
try:
    f_co2 = open('co2eq_baseline.txt', 'r')
    f_tvoc = open('tvoc_baseline.txt', 'r')

    co2_baseline = int(f_co2.read())
    tvoc_baseline = int(f_tvoc.read())
    
    #Use them to calibrate the sensor
    sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

    f_co2.close()
    f_tvoc.close()

    has_baseline = True
except:
    print('Impossible to read SGP30 baselines!')

#Store the time at which last baseline has been saved
baseline_time = time.time()

# Configure PICO SPI
spi = machine.SPI(0, baudrate=40000000, sck=machine.Pin(2), mosi=machine.Pin(3))
display = ili9225.ILI9225(spi, ss_pin=5, rs_pin=4, rst_pin=6, rotation=1)
display.clear()
display.print(str('PM2.5'),first_column,0, myfont20sb, align=ili9225.ALIGN_LEFT,x2=display.width, fg_color=0xeb348f)
display.print(str('CH20'), first_column, 30, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=0x0000FF)
display.print(str('TVOC'),first_column,60, myfont20sb, align=ili9225.ALIGN_LEFT,x2=display.width, fg_color=0x34ebb4)
display.print(str('CO2eq'), first_column,90, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=0xe5eb34)
display.print(str('Temp.'),first_column,120, myfont20sb, align=ili9225.ALIGN_LEFT,x2=display.width, fg_color=0x34ebb4)
display.print(str('RH'), first_column, 150, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=0xf50591)


COLOR_GOOD = 0x3deb34
COLOR_MEDIUM = 0xebdc34
COLOR_BAD = 0xf51105

def color(value, min_threshold, max_threshold):
        if value <= min_threshold:
            return COLOR_GOOD
        elif (value >min_threshold) and (value<=max_threshold):
            return COLOR_MEDIUM
        else:
            return COLOR_BAD    

while True:
    co2eq, tvoc = sgp30.iaq_measure()

    quality = pms5003.read()
 
    
    pmLevel = quality.data[1]
    CH2OLevel = quality.data[12]/1000
    
    pmColor = color(pmLevel, min_threshold=50, max_threshold=100)
    CH2OColor = color(CH2OLevel, min_threshold=50, max_threshold=123)
    TVOCColor = color(tvoc, min_threshold=220, max_threshold=660)
    CO2Color = color(co2eq, min_threshold=1000, max_threshold=2000)   
    
    display.print(str("{:.2f}".format(pmLevel)+' ug/m3'), second_column, 0, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=pmColor)
    display.print(str("{:.2f}".format(CH2OLevel)+' mg/m3'), second_column, 30, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=CH2OColor)
    display.print(str("{:.2f}".format(tvoc) +' ppb'), second_column, 60, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=TVOCColor)
    display.print(str("{:.2f}".format(co2eq) +' ppm'), second_column, 90, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=CO2Color)
    display.print(str("{:.2f}".format(quality.data[13]/10)+' C'), second_column, 120, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=0x34ebb4)
    display.print(str("{:.2f}".format(quality.data[14]/10)+' %'), second_column, 150, myfont20sb, align=ili9225.ALIGN_LEFT, x2=display.width, fg_color=0xf50591)
    

# Baselines should be saved after 12 hour the first timen then every hour,
    # according to the doc.
    if (has_baseline and (time.time() - baseline_time >= 3600)) \
            or ((not has_baseline) and (time.time() - baseline_time >= 43200)):

        print('Saving baseline!')
        baseline_time = time.time()

        try:
            f_co2 = open('co2eq_baseline.txt', 'w')
            f_tvoc = open('tvoc_baseline.txt', 'w')

            bl_co2, bl_tvoc = sgp30.get_iaq_baseline()
            f_co2.write(str(bl_co2))
            f_tvoc.write(str(bl_tvoc))

            f_co2.close()
            f_tvoc.close()

            has_baseline = True
        except:
            print('Impossible to write SGP30 baselines!')

    #A measurement should be done every 60 seconds, according to the doc.
    time.sleep(1)
