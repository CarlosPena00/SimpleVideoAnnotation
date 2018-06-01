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
    videoName = 'atHome008.webm'
    
    if os.path.exists(videoName):
        print ("Video path not provided, using default")
    else:
        sys.exit("Error: Video path not provided and default doesnt exist")

foldName = videoName.split('.')[0]
foldLabel = foldName + '/labels'
foldJpeg = foldName + '/JPEGImages'
foldGT = foldName + '/Ground'
foldAugment = foldJpeg

if not os.path.exists(foldName):
    os.mkdir(foldName)
if not os.path.exists(foldLabel):
    os.mkdir(foldLabel)
if not os.path.exists(foldJpeg):
    os.mkdir(foldJpeg)
if not os.path.exists(foldGT):
    os.mkdir(foldGT)
if not os.path.exists(foldAugment):
    os.mkdir(foldAugment)
          
drawRect = False
startRect = []
endRect = []
iClass = []
key = -1
color = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(0, 51, 102), (102, 51, 0),(0,0,0),(255,255,255)]
secColor = [(int(i * 0.7), int(j * 0.7), int(k * 0.7)) for (i,j,k) in color]
color.extend(secColor)
shiftColor = 10
actual = 0
lenBbox = 0

def draw(event,x,y,flags,param):
    global drawRect
    global startRect
    global frame
    global endRect
    global oriFrame
    global key
    global color
    global actual
    global lenBbox
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawRect = True
        startRect.append((x, y))
        endRect.append((x, y))
        iClass.append(cv2.getTrackbarPos('ID','VideoTag'))
        lenBbox = len(startRect)
        actual = lenBbox
    
    elif event == cv2.EVENT_MOUSEWHEEL:
        if actual > 0: 
            iClass[actual-1] = (iClass[actual-1] + 1 ) % NUM_OF_CLASS 
           
    elif event == cv2.EVENT_LBUTTONUP:
        drawRect = False
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawRect:
            endRect[actual-1] = (x, y)
            frame = oriFrame.copy()
            
    elif event == cv2.EVENT_RBUTTONDOWN:
        frame = oriFrame.copy()
        if len(startRect) > 0:
            startRect.pop()
        if len(endRect) > 0:
            endRect.pop()
        if len(iClass) > 0:
            iClass.pop()
        if actual > 0:
            actual -= 1

def imview(src, bbox):
    height, width, _ = src.shape
    # ID, xcenter/widht, ycenter/height, srcwidth/width, srcheight/height
    iClass, xYolo, yYolo, widthYolo, heightYolo = bbox
    xCenter = int( xYolo * width )
    yCenter = int( yYolo * height )
    objWidth = int( widthYolo * width )
    objHeight = int ( heightYolo * height )
        
    ul = (xCenter - objWidth/2, yCenter - objHeight/2)
    br = (xCenter + objWidth/2, yCenter + objHeight/2)
        
    cv2.rectangle(src,ul, br, (0,255,0),3)
    
    cv2.imshow("src", src)
    cv2.waitKey(10000)    
    cv2.destroyAllWindows()
    # bbox = (2, 0.79765625, 0.705208333333, 0.1015625 ,0.202083333333)
    # src = cv2.imread('/home/kaka/Desktop/SimpleVideoAnnotation/atHome004/JPEGImages/000000.jpg')
    
def VOCtoRect(vocLabel, imgW=1024, imgH=640):
    """
        vocLabel: 
             Classe; 
             absoluteX/imgWidth; absoluteY/imgHeight;
             absoluteWidth/imgWidth; absoluteHeight/imgHeigh 
    """
    xMean = vocLabel[1] * imgW
    yMean = vocLabel[2] * imgH
    
    deltaX = vocLabel[3] * imgW
    deltaY = vocLabel[4] * imgH
    
    dX = deltaX/2
    dY = deltaY/2
    xMin = int(xMean - dX)
    xMax = int(xMean + dX)
    yMin = int(yMean - dY)
    yMax = int(yMean + dY)
    
    return ([(xMin, yMin), (xMax, yMax)])


def nothing(x):
    pass

NUM_OF_CLASS = (10-1)

cv2.namedWindow("VideoTag", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("VideoTag", draw)
cv2.createTrackbar("ID", "VideoTag",0, NUM_OF_CLASS, nothing)
cv2.createTrackbar("Jump", "VideoTag",1, 10, nothing)
cv2.createTrackbar("SkipFrames", "VideoTag",1, 300, nothing)

cap = cv2.VideoCapture(videoName)
if not cap.isOpened():
    print ("Video not found or Opencv without ffmpeg")      
framePos = 0
ret, oriFrame = cap.read()     

frame = oriFrame.copy()
height, width, _ = frame.shape
oldId = 0
actualId = 0

while( cap.isOpened() and ret ):
    frame = oriFrame.copy()
    jump = cv2.getTrackbarPos('Jump','VideoTag')
    for values in range(0, len(startRect)):
        if values == actual-1:
            col = color[iClass[values]]
            thick = 2
        else:
            col = color[iClass[values] + shiftColor]
            thick = 3
        cv2.rectangle(frame, startRect[values], endRect[values], col, thick)

    cv2.imshow("VideoTag", frame)

    key = (cv2.waitKey(1) & 0xFF)
    if key == 255:
        continue
    if key == ord('q'):
        break    
    if actual <= len(startRect) and actual > 0 :
        if key == ord('w'):
            startRect[actual-1] = (startRect[actual-1][0], startRect[actual-1][1]-jump)
            endRect[actual-1] = (endRect[actual-1][0], endRect[actual-1][1]-jump)
        if key == ord('s'):
            startRect[actual-1] = (startRect[actual-1][0], startRect[actual-1][1]+jump)
            endRect[actual-1] = (endRect[actual-1][0], endRect[actual-1][1]+jump)
        if key == ord('a'):
            startRect[actual-1] = (startRect[actual-1][0]-jump, startRect[actual-1][1])
            endRect[actual-1] = (endRect[actual-1][0]-jump, endRect[actual-1][1])
        if key == ord('d'):
            startRect[actual-1] = (startRect[actual-1][0]+jump, startRect[actual-1][1])
            endRect[actual-1] = (endRect[actual-1][0]+jump, endRect[actual-1][1])
        if key == ord('6'):
            startRect[actual-1] = (startRect[actual-1][0]-jump, startRect[actual-1][1])
            endRect[actual-1] = (endRect[actual-1][0]+jump, endRect[actual-1][1])
        if key == ord('4'):
            startRect[actual-1] = (startRect[actual-1][0]+jump, startRect[actual-1][1])
            endRect[actual-1] = (endRect[actual-1][0]-jump, endRect[actual-1][1])
        if key == ord('8'):
            startRect[actual-1] = (startRect[actual-1][0], startRect[actual-1][1]-jump)
            endRect[actual-1] = (endRect[actual-1][0], endRect[actual-1][1]+jump)
        if key == ord('5'):
            startRect[actual-1] = (startRect[actual-1][0], startRect[actual-1][1]+jump)
            endRect[actual-1] = (endRect[actual-1][0], endRect[actual-1][1]-jump)
        
        if key == ord('*'):
            iClass[actual-1] = (iClass[actual-1] + 1 ) % NUM_OF_CLASS 
        if key == ord('/'):
            iClass[actual-1] = (iClass[actual-1] - 1 ) % NUM_OF_CLASS 
            
        if key == ord('-'):
            del startRect[actual-1]
            del endRect[actual-1]
            del iClass[actual-1]

            if(actual < 0): actual = 0
            lenBbox = len(startRect)
            
            
    if key == ord('9'):
        actual = ((actual)%(lenBbox)) + 1

    if key == ord('7'):
        actual -= 1
        if actual == 0:
            actual = lenBbox
        
    if key == ord('z'):
        skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
        actualPosFrame = cap.get(flagCapturePosFrame)
        newFramePos = actualPosFrame-skip
        if newFramePos < 0:
            newFramePos = 0
        
        cap.set(flagCapturePosFrame, newFramePos)
        ret, oriFrame = cap.read() 
        
        framePos -= 1
        if framePos < 0:
            framePos = 0   
    
    if key == ord('r'):
        if (os.path.exists(foldLabel + '/000000.txt')):
            startRect, endRect, iClass = [], [], []
            actual = 0
            
            with open(foldLabel+"/{:06d}.txt".format(framePos), 'r') as f:
                for line in f.readlines():
                    voc = [float(i) for i in line.split()]
                    rect = VOCtoRect(voc, width, height)
                    iClass.append(int(voc[0]))
                    startRect.append(rect[0])
                    endRect.append(rect[1])
                    lenBbox = len(startRect)
                    actual = 1
                    
    if key == (32):
        vocLabel = []
        flipLabel = []
        rotLabel = []
        save = False
        for values in range(0,len(startRect)):
            frameWidth, frameHeight = abs(startRect[values][0]-endRect[values][0]), abs(startRect[values][1]-endRect[values][1])
            xCenter, yCenter = abs((startRect[values][0]+endRect[values][0])/2.0), abs((startRect[values][1]+endRect[values][1])/2.0)
            xVoc, yVoc = xCenter/width, yCenter/height
                        
            if frameWidth < 4 or frameHeight < 4:
                continue
            save = True
            widthVoc = float(frameWidth)/width
            heightVoc = float(frameHeight)/height
            vocClass = (iClass[values], xVoc,yVoc,  widthVoc, heightVoc, '\n')
            vocLabel.append(' '.join(str(e) + '' for e in vocClass))
        
            flipClass = (iClass[values], 1-xVoc,yVoc,  widthVoc, heightVoc, '\n')
            flipLabel.append(' '.join(str(e) + '' for e in flipClass))
            
            rotX = (height - yCenter)/height
            rotY = xVoc
            rotClass = (iClass[values], rotX, rotY, heightVoc, widthVoc, '\n')
            rotLabel.append(' '.join(str(e) + '' for e in rotClass))
        
        if save == False:
            ret, oriFrame = cap.read() 
            continue
        
        fileName = "/{:06d}.jpg".format(framePos)
        cv2.imwrite(foldGT+fileName, frame)
        cv2.imwrite(foldJpeg+fileName, oriFrame)
        
        ###
        fileName = "/{:06d}_F.jpg".format(framePos)
        flip = cv2.flip(oriFrame, 1)
        cv2.imwrite(foldAugment+fileName, flip)
        ###
        fileName = "/{:06d}_R.jpg".format(framePos)
        rot = cv2.rotate(oriFrame, 0)
        cv2.imwrite(foldAugment+fileName, rot)
        

        with open(foldLabel+"/{:06d}.txt".format(framePos), 'w') as f:
            for labels in vocLabel:
                f.write(labels)
        
        with open(foldLabel+"/{:06d}_F.txt".format(framePos), 'w') as f:
            for labels in flipLabel:
                f.write(labels)
                
        with open(foldLabel+"/{:06d}_R.txt".format(framePos), 'w') as f:
            for labels in rotLabel:
                f.write(labels)

        actualPosFrame = cap.get(flagCapturePosFrame)
        skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
        cap.set(flagCapturePosFrame,actualPosFrame+skip)
        ret, oriFrame = cap.read()
        framePos += 1
        oldId = actualId
    

command = 'ls -d '+ os.getcwd() +'/{}/JPEGImages/* > '.format(foldName) + os.getcwd() + '/{}/imgList.txt'.format(foldName)
os.system(command)


cap.release()
cv2.destroyAllWindows()

