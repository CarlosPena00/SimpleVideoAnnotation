#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 13:48:53 2018

@author: kaka
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

videoName = 'Mug4.webm'
cap = cv2.VideoCapture(videoName)
if not cap.isOpened():
    print "Video not found or Opencv without ffmpeg"
amount_of_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
actual = cap.get(cv2.CAP_PROP_POS_FRAMES)
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
    global Oriframe
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
            frame = Oriframe.copy()
            iClass = cv2.getTrackbarPos('ID','VideoTag')
            cv2.rectangle(frame, startRect, endRect, color[iClass])
    elif event == cv2.EVENT_RBUTTONDOWN:
        frame = Oriframe.copy()
        startRect = (-1, -1)
        endRect = (-1, -1)

def nothing(x):
    pass

cv2.namedWindow("VideoTag")
cv2.setMouseCallback("VideoTag", draw)
cv2.createTrackbar("ID", "VideoTag",0, 7, nothing)
cv2.createTrackbar("Jump", "VideoTag",1, 10, nothing)
cv2.createTrackbar("SkipFrames", "VideoTag",1, 300, nothing)
        
framePos = 0
ret, Oriframe = cap.read()     
frame = Oriframe.copy()
height, width, _ = frame.shape



while(cap.isOpened() and type(Oriframe) is not type(None) ):

    frame = Oriframe.copy()
    iClass = cv2.getTrackbarPos('ID','VideoTag')
    Jump = cv2.getTrackbarPos('Jump','VideoTag')
    
    cv2.rectangle(frame, startRect, endRect, color[iClass], 2)
    cv2.imshow("VideoTag", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
    if key == ord('w'):
        startRect = (startRect[0], startRect[1]-Jump)
        endRect = (endRect[0], endRect[1]-Jump)
    if key == ord('s'):
        startRect = (startRect[0], startRect[1]+Jump)
        endRect = (endRect[0], endRect[1]+Jump)
    if key == ord('a'):
        startRect = (startRect[0]-Jump, startRect[1])
        endRect = (endRect[0]-Jump, endRect[1])
    if key == ord('d'):
        startRect = (startRect[0]+Jump, startRect[1])
        endRect = (endRect[0]+Jump, endRect[1])
    
    if key == ord('6'):
        startRect = (startRect[0]-Jump, startRect[1])
        endRect = (endRect[0]+Jump, endRect[1])
    if key == ord('4'):
        startRect = (startRect[0]+Jump, startRect[1])
        endRect = (endRect[0]-Jump, endRect[1])
    if key == ord('8'):
        startRect = (startRect[0], startRect[1]-Jump)
        endRect = (endRect[0], endRect[1]+Jump)
    if key == ord('5'):
        startRect = (startRect[0], startRect[1]+Jump)
        endRect = (endRect[0], endRect[1]-Jump)
    if key == 32:
        frameWid, frameHei = abs(startRect[0]-endRect[0]), abs(startRect[1]-endRect[1])
        xCenter, yCenter = abs((startRect[0]+endRect[0])/2.0), abs((startRect[1]+endRect[1])/2.0)
        xVoc, yVoc = xCenter/width, yCenter/height
        
        actual = cap.get(cv2.CAP_PROP_POS_FRAMES)
        skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
        cap.set(cv2.CAP_PROP_POS_FRAMES,actual+skip)
        
        if frameWid < 2 or frameHei <2:
            ret, Oriframe = cap.read()  
            continue
        
        widVoc = float(frameWid)/width
        heiVoc = float(frameHei)/height
        iClass = cv2.getTrackbarPos('ID','VideoTag')
        vocClass = (iClass, xVoc,yVoc, widVoc, heiVoc, '\n')
        vocLabel = ' '.join(str(e) + ' ' for e in vocClass)
        fileName = "/{:06d}.jpg".format(framePos)
        cv2.imwrite(foldGT+fileName, frame)
        fileName = "/{:06d}.jpg".format(framePos)
        cv2.imwrite(foldJpeg+fileName, Oriframe)
                
        ret, Oriframe = cap.read()  
        
        with open(foldLabel+"/{:06d}.txt".format(framePos), 'w') as f:
            f.write(vocLabel)
        framePos += 1


command = 'ls -d '+os.getcwd()+'/{}/JPEGImages/* > '.format(foldName)+os.getcwd()+'/{}/imgList.txt'.format(foldName)
os.system(command)

    
cap.release()
cv2.destroyAllWindows()

