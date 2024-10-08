# RP2240-Zero-air-monitor

## Version V2
I replaced the SHT31 of adafruit by a cheaper version. I also added the air quality sensor SGP30. 

![Model](https://github.com/hongloan/RP2240-Zero-air-monitor/blob/main/thumbnail.png)

All the components are now mounted on the DIY board following the circuit

![Model](https://github.com/hongloan/RP2240-Zero-air-monitor/blob/main/RP2040ZeroOledSGP30_bb.png)

You will need to use the code

  **oledSht31Sgp30.py**
  
and also install the library **adafruit_sgp30**

## Version V1
In this project, I used microcontroller to monitor the humidity and temperature of 2 different locations. The measured data is shown on SSD1306 oled screen.

![Model](https://github.com/hongloan/RP2240-Zero-air-monitor/blob/main/image1-7.png)

There are some libraries that we need to import
  
  **ssd1306.py** for the oled screen
  
  **sth31.py** for the sht31 sensor
  
  **oled.py** to change the font size

The main code for RP2040-zero is oled2SensorBigText.py. The most important part is the setting for the I2C buses. I2C0 is shared between 2 SHT31 sensors (line 14). One of them has the ADR pin connected to Vcc to set the I2C address to 0x45 (line 16). The other one will have 0x44 (line 15) instead (default). I2C1 is used for oled screen SSD1306 (line 19).

