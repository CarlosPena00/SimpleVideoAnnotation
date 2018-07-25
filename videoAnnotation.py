#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import cv2
import os
import sys

class VideoAnnotation:
    def __init__(self, videoName='RM4.mp4'):

        ## Check opencv version to define how to get frames
        self.flagCapturePosFrame = 0
        self.videoName = ''

        cv2v = cv2.__version__
        if(cv2v[0] >= '3'):
            self.flagCapturePosFrame = cv2.CAP_PROP_POS_FRAMES
        elif(cv2v[0] == '2'):
            self.flagCapturePosFrame = cv2.cv.CV_CAP_PROP_POS_FRAMES

        if(videoName == 'RM4.mp4'):
            print ("Example of usage: python VideoAnnotation.py video.mp4")

            if os.path.exists(videoName):
                print ("Video path not provided, using default")
            else:
                sys.exit("Error: Video path not provided and default doesnt exist")
        else:
            self.videoName = videoName

        ## Create folders to save
        self.folderName = videoName.split('.')[0]
        self.folderLabel = self.folderName + '/labels'
        self.folderJpeg = self.folderName + '/JPEGImages'
        self.folderGT = self.folderName + '/Ground'
        self.folderAugment = self.folderJpeg

        if not os.path.exists(self.folderName):
            os.mkdir(self.folderName)
        if not os.path.exists(self.folderLabel):
            os.mkdir(self.folderLabel)
        if not os.path.exists(self.folderJpeg):
            os.mkdir(self.folderJpeg)
        if not os.path.exists(self.folderGT):
            os.mkdir(self.folderGT)
        if not os.path.exists(self.folderAugment):
            os.mkdir(self.folderAugment)

        self.drawRect = False
        self.startRect = []
        self.endRect = []
        self.iClass = []
        self.key = -1
        self.color = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(0, 51, 102), (102, 51, 0),(0,0,0),(255,255,255)]
        self.secColor = [(int(i * 0.7), int(j * 0.7), int(k * 0.7)) for (i,j,k) in self.color]
        self.color.extend(self.secColor)
        self.shiftColor = 10
        self.actual = 0
        self.lenBbox = 0
        self.lastFrameSkip = 0

        self.num_of_classes = (10-1)

        self.ret = None
        self.oriFrame = None

    def draw(self,event,x,y,flags,param):
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawRect = True
            self.startRect.append((x, y))
            self.endRect.append((x, y))
            self.iClass.append(cv2.getTrackbarPos('ID','VideoTag'))
            self.lenBbox = len(self.startRect)
            self.actual = self.lenBbox
        
        elif event == cv2.EVENT_MOUSEWHEEL:
            if self.actual > 0: 
                self.iClass[self.actual-1] = (self.iClass[self.actual-1] + 1 ) % self.num_of_classes 
               
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawRect = False
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawRect:
                self.endRect[self.actual-1] = (x, y)
                frame = self.oriFrame.copy()
                
        elif event == cv2.EVENT_RBUTTONDOWN:
            frame = self.oriFrame.copy()
            if len(self.startRect) > 0:
                self.startRect.pop()
            if len(self.endRect) > 0:
                self.endRect.pop()
            if len(self.iClass) > 0:
                self.iClass.pop()
            if self.actual > 0:
                self.actual -= 1

    def imview(self,src, bbox):

        height, width, _ = src.shape
        # ID, xcenter/widht, ycenter/height, srcwidth/width, srcheight/height
        self.iClass, xYolo, yYolo, widthYolo, heightYolo = bbox
        xCenter = int( xYolo * width )
        yCenter = int( yYolo * height )
        objWidth = int( widthYolo * width )
        objHeight = int ( heightYolo * height )

        ul = (xCenter - objWidth/2, yCenter - objHeight/2)
        br = (xCenter + objWidth/2, yCenter + objHeight/2)

        cv2.rectangle(src,ul, br, (0,255,0),3)
        cv2.imshow("src", src)
        cv2.waitself.Key(10000)    
        cv2.destroyAllWindows()
        # bbox = (2, 0.79765625, 0.705208333333, 0.1015625 ,0.202083333333)
        # src = cv2.imread('/home/kaka/Desktop/SimpleVideoAnnotation/atHome004/JPEGImages/000000.jpg')


    def VOCtoRect(self,vocLabel, imgW=1024, imgH=640):
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


    def nothing(self,x):
        pass


    def doEverything(self):

        cv2.namedWindow("VideoTag", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("VideoTag", self.draw)
        cv2.createTrackbar("ID", "VideoTag",0, self.num_of_classes, self.nothing)
        cv2.createTrackbar("Jump", "VideoTag",1, 10, self.nothing)
        cv2.createTrackbar("SkipFrames", "VideoTag",1, 300, self.nothing)

        cap = cv2.VideoCapture(self.videoName)
        if not cap.isOpened():
            print ("Video not found or Opencv without ffmpeg")      
        self.framePos = 0
        self.ret, self.oriFrame = cap.read()     

        frame = self.oriFrame.copy()
        height, width, _ = frame.shape
        oldId = 0
        self.actualId = 0

        while( cap.isOpened() and self.ret ):
            frame = self.oriFrame.copy()
            jump = cv2.getTrackbarPos('Jump','VideoTag')
            for values in range(0, len(self.startRect)):
                if values == self.actual-1:
                    col = self.color[self.iClass[values]]
                    thick = 2
                else:
                    col = self.color[self.iClass[values] + self.shiftColor]
                    thick = 2
                cv2.rectangle(frame, self.startRect[values], self.endRect[values], col, thick)

            cv2.imshow("VideoTag", frame)

            self.key = (cv2.waitKey(1) & 0xFF)
            if self.key == 255:
                continue
            if self.key == ord('q'):
                break    
            if self.actual <= len(self.startRect) and self.actual > 0 :
                if self.key == ord('w'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0], self.startRect[self.actual-1][1]-jump)
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0], self.endRect[self.actual-1][1]-jump)
                if self.key == ord('s'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0], self.startRect[self.actual-1][1]+jump)
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0], self.endRect[self.actual-1][1]+jump)
                if self.key == ord('a'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0]-jump, self.startRect[self.actual-1][1])
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0]-jump, self.endRect[self.actual-1][1])
                if self.key == ord('d'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0]+jump, self.startRect[self.actual-1][1])
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0]+jump, self.endRect[self.actual-1][1])
                if self.key == ord('6'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0]-jump, self.startRect[self.actual-1][1])
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0]+jump, self.endRect[self.actual-1][1])
                if self.key == ord('4'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0]+jump, self.startRect[self.actual-1][1])
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0]-jump, self.endRect[self.actual-1][1])
                if self.key == ord('8'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0], self.startRect[self.actual-1][1]-jump)
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0], self.endRect[self.actual-1][1]+jump)
                if self.key == ord('5'):
                    self.startRect[self.actual-1] = (self.startRect[self.actual-1][0], self.startRect[self.actual-1][1]+jump)
                    self.endRect[self.actual-1] = (self.endRect[self.actual-1][0], self.endRect[self.actual-1][1]-jump)
                
                if self.key == ord('*'):
                    self.iClass[self.actual-1] = (self.iClass[self.actual-1] + 1 ) % self.num_of_classes 
                if self.key == ord('/'):
                    self.iClass[self.actual-1] = (self.iClass[self.actual-1] - 1 ) % self.num_of_classes 
                
                if self.key == ord('c'):
                    self.startRect.append(self.startRect[-1])
                    self.endRect.append(self.endRect[-1])
                    self.iClass.append(self.iClass[-1])
                    self.lenBbox = len(self.startRect)
                    self.actual = self.lenBbox
                    
                if self.key == ord('-'):
                    del self.startRect[self.actual-1]
                    del self.endRect[self.actual-1]
                    del self.iClass[self.actual-1]

                    if(self.actual < 0): self.actual = 0
                    self.lenBbox = len(self.startRect)
                    
                    
            if self.key == ord('9') and self.lenBbox > 0:
                self.actual = ((self.actual)%(self.lenBbox)) + 1

            if self.key == ord('7') and self.lenBbox > 0:
                self.actual -= 1
                if self.actual == 0:
                    self.actual = self.lenBbox
                
            if self.key == ord('z'):
                skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
                self.actualPosFrame = cap.get(flagCapturePosFrame)
                newFramePos = self.actualPosFrame-skip
                if newFramePos < 0:
                    newFramePos = 0
                
                cap.set(self.flagCapturePosFrame, newFramePos)
                self.ret, self.oriFrame = cap.read() 
                
                self.framePos -= 1
                if self.framePos < 0:
                    self.framePos = 0   
            
            if self.key == ord('r'):
                path_r = self.folderLabel+"/{:06d}.txt".format(self.framePos)
                if (not os.path.exists(path_r)):
                    path_r = self.folderLabel + '/000000.txt'
                if (os.path.exists(path_r)):
                    self.startRect, self.endRect, self.iClass = [], [], []
                    self.actual = 0
                    
                    with open(path_r, 'r') as f:
                        lines = f.readlines()
                        for line in sorted(lines, key=lambda t: t[2:]):
                            voc = [float(i) for i in line.split()]
                            rect = self.VOCtoRect(voc, width, height)
                            self.iClass.append(int(voc[0]))
                            self.startRect.append(rect[0])
                            self.endRect.append(rect[1])
                            self.lenBbox = len(self.startRect)
                            self.actual = 1
                            
            if self.key == (32):
                vocLabel = []
                flipLabel = []
                rotLabel = []
                save = False
                for values in range(0,len(self.startRect)):
                    frameWidth, frameHeight = abs(self.startRect[values][0]-self.endRect[values][0]), abs(self.startRect[values][1]-self.endRect[values][1])
                    xCenter, yCenter = abs((self.startRect[values][0]+self.endRect[values][0])/2.0), abs((self.startRect[values][1]+self.endRect[values][1])/2.0)
                    xVoc, yVoc = xCenter/width, yCenter/height
                                
                    if frameWidth < 4 or frameHeight < 4:
                        continue
                    save = True
                    widthVoc = float(frameWidth)/width
                    heightVoc = float(frameHeight)/height
                    vocClass = (self.iClass[values], xVoc,yVoc,  widthVoc, heightVoc, '\n')
                    vocLabel.append(' '.join(str(e) + '' for e in vocClass))
                
                    flipClass = (self.iClass[values], 1-xVoc,yVoc,  widthVoc, heightVoc, '\n')
                    flipLabel.append(' '.join(str(e) + '' for e in flipClass))
                    
                    rotX = (height - yCenter)/height
                    rotY = xVoc
                    rotClass = (self.iClass[values], rotX, rotY, heightVoc, widthVoc, '\n')
                    rotLabel.append(' '.join(str(e) + '' for e in rotClass))
                
                if save == False:
                    self.actualPosFrame = cap.get(flagCapturePosFrame)
                    skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
                    if (self.actualPosFrame+skip > self.lastFrameSkip):
                        cap.set(flagCapturePosFrame,self.actualPosFrame+skip)
                        self.ret, self.oriFrame = cap.read() 
                        self.lastFrameSkip = self.actualPosFrame+skip
                    else:
                        self.ret = False;
                    continue
                
                fileName = "/{:06d}.jpg".format(self.framePos)
                cv2.imwrite(self.folderGT+fileName, frame)
                cv2.imwrite(self.folderJpeg+fileName, self.oriFrame)
                
                ###
                fileName = "/{:06d}_F.jpg".format(self.framePos)
                flip = cv2.flip(self.oriFrame, 1)
                cv2.imwrite(self.folderAugment+fileName, flip)
                ###
                fileName = "/{:06d}_R.jpg".format(self.framePos)
                rot = cv2.rotate(self.oriFrame, 0)
                cv2.imwrite(self.folderAugment+fileName, rot)
                

                with open(self.folderLabel+"/{:06d}.txt".format(self.framePos), 'w') as f:
                    for labels in vocLabel:
                        f.write(labels)
                
                with open(self.folderLabel+"/{:06d}_F.txt".format(self.framePos), 'w') as f:
                    for labels in flipLabel:
                        f.write(labels)
                        
                with open(self.folderLabel+"/{:06d}_R.txt".format(self.framePos), 'w') as f:
                    for labels in rotLabel:
                        f.write(labels)

                self.actualPosFrame = cap.get(self.flagCapturePosFrame)
                skip = cv2.getTrackbarPos('SkipFrames','VideoTag')
                if (self.actualPosFrame+skip > self.lastFrameSkip):
                    cap.set(self.flagCapturePosFrame,self.actualPosFrame+skip)
                    self.ret, self.oriFrame = cap.read() 
                    self.lastFrameSkip = self.actualPosFrame+skip
                else:
                    self.ret = False;
                self.framePos += 1
                oldId = self.actualId
            

        command = 'ls -d '+ os.getcwd() +'/{}/JPEGImages/* > '.format(self.folderName) + os.getcwd() + '/{}/imgList.txt'.format(self.folderName)
        os.system(command)


        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    videAnnotation = VideoAnnotation(videoName="atHome001.webm")
    videAnnotation.doEverything()