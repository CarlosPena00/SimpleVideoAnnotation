# SimpleVideoAnnotation

> A simple Video annotation made with python + opencv for detection in yolo-voc format

![](VideoTag.png)

## Installation

```sh
	#TODO
	You will need OpenCV with ffmpeg lib
```

## Usage example

```sh
	python VideoAnnotation.py
```

## Controls:

* q - quit
* Mouse Left - Create New Bound Box, drag to change the dim
* Mouse right - Erase actual Bounding Box
* WASD - move the Bound Box
* 8456 - Change width height
* Space - next frame

## Variables -- Trackbar

* ID - Id of the label 
* Jump - How many pixels WASD/8456 will change
* Skip - How many frames will be skiped

## Tree
Givem a video file, it will create:

```
.
└── VideoFolder (the same name of the video file)
    ├── Ground  (Fold with ground imagens, with Bound Box)
    ├── JPEGImages (Fold with the imagens, without Bound Box)
    ├── labels (Fold with the txt labels files in yolo-voc format)
 	└──	imgList.txt (List with full directory of all JPEGImages)

```

### Label Format

     ID; 
     absoluteX/imgWidth; absoluteY/imgHeight;
     absoluteWidth/imgWidth; absoluteHeight/imgHeigh  

### TODO
	
	1. Organize the code
	2. Add suport for multi bound box in the same image
	3. Make automatic Bound Box
