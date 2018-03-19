#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import cv2
import os
import sys

cv2v = cv2.__version__
if(cv2v[0] >= '3'):
    flagCapturePosFrame = cv2.CAP_PROP_POS_FRAMES
elif(cv2v[0] == '2'):
    flagCapturePosFrame = cv2.cv.CV_CAP_PROP_POS_FRAMES


if len(sys.argv) == 2:
    videoName = sys.argv[1]
else:
    print ("Example of usage: python VideoAnnotation.py video.mp4")
    videoName = 'Mug4.webm'
    
    if os.path.exists(videoName):
        print ("Video path not provided, using default")
    else:
        sys.exit("Error: Video path not provided and default doesnt exist")

foldName = videoName.split('.')[0]
foldLabel = foldName+'/labels'
foldJpeg = foldName+'/JPEGImages'
foldGT = foldName+'/Ground'

if not os.path.exists(foldName):
    os.mkdir(foldName)
if not os.path.exists(foldLabel):
    os.mkdir(foldLabel)
if not os.path.exists(foldJpeg):
    os.mkdir(foldJpeg)
if not os.path.exists(foldGT):
    os.mkdir(foldGT)
          
drawRect = False
startRect = (-1, -1)
endRect = (-1, -1)
key = -1
color = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(0,0,0),(255,255,255)]

def draw(event,x,y,flags,param):
    global drawRect
    global startRect
    global frame
    global endRect
    global oriFrame
    global key
    global color
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawRect = True
        startRect = (x, y)
        endRect = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawRect = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawRect:
            endRect = (x, y)
            frame = oriFrame.copy()
            iClass = cv2.getTrackbarPos('ID','VideoTag')
            cv2.rectangle(frame, startRect, endRect, color[iClass])
    elif event == cv2.EVENT_RBUTTONDOWN:
        frame = oriFrame.copy()
        startRect = (-1, -1)
        endRect = (-1, -1)

def nothing(x):
    pass

cv2.namedWindow("VideoTag")
cv2.setMouseCallback("VideoTag", draw)
cv2.createTrackbar("ID", "VideoTag",0, 7, nothing)
cv2.createTrackbar("Jump", "VideoTag",1, 10, nothing)
cv2.createTrackbar("SkipFrames", "VideoTag",1, 300, nothing)

cap = cv2.VideoCapture(videoName)
if not cap.isOpened():
    print ("Video not found or Opencv without ffmpeg")      
framePos = 0
ret, oriFrame = cap.read()     

frame = oriFrame.copy()
height, width, _ = frame.shape

while(cap.isOpened() and ret ):

    frame = oriFrame.copy()
    iClass = cv2.getTrackbarPos('ID','VideoTag')
    jump = cv2.getTrackbarPos('Jump','VideoTag')
    
    cv2.rectangle(frame, startRect, endRect, color[iClass], 2)
    cv2.imshow("VideoTag", frame)

    key = (cv2.waitKey(1) & 0xFF)
    if key == ord('q'):
        break
    if key == ord('w'):
        startRect = (startRect[0], startRect[1]-jump)
        endRect = (endRect[0], endRect[1]-jump)
    if key == ord('s'):
        startRect = (startRect[0], startRect[1]+jump)
        endRect = (endRect[0], endRect[1]+jump)
    if key == ord('a'):
        startRect = (startRect[0]-jump, startRect[1])
        endRect = (endRect[0]-jump, endRect[1])
    if key == ord('d'):
        startRect = (startRect[0]+jump, startRect[1])
        endRect = (endRect[0]+jump, endRect[1])
    if key == ord('6'):
        startRect = (startRect[0]-jump, startRect[1])
        endRect = (endRect[0]+jump, endRect[1])
    if key == ord('4'):
        startRect = (startRect[0]+jump, startRect[1])
        endRect = (endRect[0]-jump, endRect[1])
    if key == ord('8'):
        startRect = (startRect[0], startRect[1]-jump)
        endRect = (endRect[0], endRect[1]+jump)
    if key == ord('2'):
        startRect = (startRect[0], startRect[1]+jump)
        endRect = (endRect[0], endRect[1]-jump)
    if key == (32):
        frameWidth, frameHeight = abs(startRect[0]-endRect[0]), abs(startRect[1]-endRect[1])
        xCenter, yCenter = abs((startRect[0]+endRect[0])/2.0), abs((startRect[1]+endRect[1])/2.0)
        xVoc, yVoc = xCenter/width, yCenter/height
        
        actual = cap.get(flagCapturePosFrame)
        skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
        cap.set(flagCapturePosFrame,actual+skip)
        
        if frameWidth < 2 or frameHeight <2:
            ret, oriFrame = cap.read()  
            continue
    
        widthVoc = float(frameWidth)/width
        heightVoc = float(frameHeight)/height
        iClass = cv2.getTrackbarPos('ID','VideoTag')
        vocClass = (iClass, xVoc,yVoc,  widthVoc, heightVoc, '\n')
        vocLabel = ' '.join(str(e) + ' ' for e in vocClass)
        fileName = "/{:06d}.jpg".format(framePos)
        cv2.imwrite(foldGT+fileName, frame)
        fileName = "/{:06d}.jpg".format(framePos)
        cv2.imwrite(foldJpeg+fileName, oriFrame)
                
        ret, oriFrame = cap.read()  
        
        with open(foldLabel+"/{:06d}.txt".format(framePos), 'w') as f:
            f.write(vocLabel)
        framePos += 1


command = 'ls -d '+ os.getcwd() +'/{}/JPEGImages/* > '.format(foldName) + os.getcwd() + '/{}/imgList.txt'.format(foldName)
os.system(command)

cap.release()
cv2.destroyAllWindows()

