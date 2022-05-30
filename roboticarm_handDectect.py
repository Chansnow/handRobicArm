#!/usr/bin/python

import cv2
import time
import math
import smbus
import serial  
import time
import numpy as np

cv2.namedWindow('手动控制台')


def nothing(x):
    pass


cv2.createTrackbar('舵机1','手动控制台',500,2000,nothing)
cv2.createTrackbar('舵机2','手动控制台',400,800,nothing)
cv2.createTrackbar('舵机3','手动控制台',250,700,nothing)
cv2.createTrackbar('舵机4','手动控制台',500,900,nothing)


cap=cv2.VideoCapture(0)

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, int(pulse))
    


if __name__=='__main__':
 
  pwm = PCA9685(0x40, debug=False)
  pwm.setPWMFreq(50)
  
  
  ser = serial.Serial('/dev/ttyAMA0', 9600)
  if ser.isOpen == False:
    ser.open()                # 打开串口
    
  while True:
   # setServoPulse(2,2500)
   
    ret,frame=cap.read()
    frame=cv2.flip(frame,0)

    count = ser.inWaiting()
    if count!=0:
        recv = ser.read(5)
        x=recv.decode()
        print(x)
        flag=int(x)%10
        y1=int(x)/10%100
        x1=int(x)/10/100
        # 清空接收缓冲区  
        ser.flushInput()  
        # 必要的软件延时  
        time.sleep(0.1)
        
        
        
        if x1>10 and x1<90 and y1>20 and y1<70:
            pwm0=20*x1+300
            pwm1=20*y1

            
            if flag==0:
                pwm3=500
            if flag==1:
                pwm3=900
                
                
            pwm.setServoPulse(0,pwm0)
            pwm.setServoPulse(1,pwm1)
            pwm.setServoPulse(2,pwm2)
            pwm.setServoPulse(3,pwm3)
            time.sleep(0.02)
        
    
    cv2.imshow('手动控制台',frame)
    cv2.waitKey(5)
    
    pwm0=cv2.getTrackbarPos('舵机1','手动控制台')
    pwm1=cv2.getTrackbarPos('舵机2','手动控制台')
    pwm2=cv2.getTrackbarPos('舵机3','手动控制台')
    pwm3=cv2.getTrackbarPos('舵机4','手动控制台')

    

    
    





