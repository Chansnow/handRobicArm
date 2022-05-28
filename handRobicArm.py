import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector   # 手部检测方法
import time
import autopy
import serial
import struct
 
#打开串口
serialPort="COM3"   #串口号
baudRate=9600       #波特率
ser=serial.Serial(serialPort,baudRate,timeout=0.5) 
ser.bytesize = 8        #设置数据位
ser.stopbits = 1        #设置停止位
ser.parity = "N"        #设置校验位
 
print("参数设置：串口=%s ，波特率=%d"%(serialPort,baudRate))#输出串口号和波特率

flag=0


#（1）导出视频数据
wScr, hScr = autopy.screen.size()   # 返回电脑屏幕的宽和高(1920.0, 1080.0)
wCam, hCam = 1280, 720   # 视频显示窗口的宽和高
pt1, pt2 = (100,100), (1100, 500)   # 虚拟鼠标的移动范围，左上坐标pt1，右下坐标pt2
 
cap = cv2.VideoCapture(0)  # 0代表自己电脑的摄像头
cap.set(3, wCam)  # 设置显示框的宽度1280
cap.set(4, hCam)  # 设置显示框的高度720
 
pTime = 0  # 设置第一帧开始处理的起始时间
 
pLocx, pLocy = 0, 0  # 上一帧时的鼠标所在位置
 
smooth = 4  # 自定义平滑系数，让鼠标移动平缓一些
 
#（2）接收手部检测方法
detector = HandDetector(mode=False,  # 视频流图像 
                        maxHands=1,  # 最多检测一只手
                        detectionCon=0.8,  # 最小检测置信度 
                        minTrackCon=0.5)   # 最小跟踪置信度
 
#（3）处理每一帧图像
while True:
    
    # 图片是否成功接收、img帧图像
    success, img = cap.read()
    
    # 翻转图像，使自身和摄像头中的自己呈镜像关系
    img = cv2.flip(img,1)  # 1代表水平翻转，0代表竖直翻转
    
    # 在图像窗口上创建一个矩形框，在该区域内移动鼠标
    cv2.rectangle(img, pt1, pt2, (0,255,255), 5)
    
    #（4）手部关键点检测
    # 传入每帧图像, 返回手部关键点的坐标信息(字典)，绘制关键点后的图像
    hands, img = detector.findHands(img, flipType=False)  # 上面反转过了，这里就不用再翻转了
    # print(hands)
    
    # 如果能检测到手那么就进行下一步
    if hands:
        
        # 获取手部信息hands中的21个关键点信息
        lmList = hands[0]['lmList']  # hands是以字典为元素的列表，hands[0]为字典，字典包每只手的关键点信息
        
        # 获取食指指尖坐标，和中指指尖坐标
        x1, y1,z1 = lmList[0]  # 手掌的关键点索引号为8
        # x2, y2,z2 = lmList[12] # 中指指尖索引12
 
        #（5）检查哪个手指是朝上的
        fingers = detector.fingersUp(hands[0])  # 传入
        print(fingers) #返回 [0,1,1,0,0] 代表 只有食指和中指竖起
        
        if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            flag=1
        else:
            flag=0
            
        print(flag)
        print(x1,y1,z1)
        
        x1=int(x1/10)
        y1=int(y1/10)
        # wdata=struct.pack("<biiib",0x1a,int(x1),int(y1),int(flag),0x2a)#<字节顺序（小端）b signed char  H unsigned int
        # ser.write(wdata)#发送数据
        #收发数据
        # data = bytes([x1, y1, flag])
        # ser.write(data)
        x1=str(x1)
        y1=str(y1)
        flag=str(flag)
        ser.write((x1+y1+flag).encode())
        # print(ser.readline())#可以接收中文

 
    #（10）显示图像
    # 查看FPS
    cTime = time.time() #处理完一帧图像的时间
    fps = 1/(cTime-pTime)
    pTime = cTime  #重置起始时间
    
    # 在视频上显示fps信息，先转换成整数再变成字符串形式，文本显示坐标，文本字体，文本大小
    cv2.putText(img, str(int(fps)), (70,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)  
    
    # 显示图像，输入窗口名及图像数据
    cv2.imshow('image', img)    
    if cv2.waitKey(1) & 0xFF==27:  #每帧滞留20毫秒后消失，ESC键退出
        break
 
# 释放视频资源
ser.close() 
cap.release()
cv2.destroyAllWindows()
