import numpy as np
from PIL import Image

def normalizeControlTape(controlTape,minPd,maxPd):
    pdRange=maxPd-minPd
    normalizedControlTape=[]
    for i in range(len(controlTape)):
        controlValue=controlTape[i]
        normalizedControlValue=(controlValue-minPd)/pdRange
        normalizedControlTape.append(normalizedControlValue)
    return normalizedControlTape

def makeColorArray(normaliedTape,minPd,maxPd):
    MAX_COLOR=255
    pdRange=maxPd-minPd
    #X=R Y=G Z=B
    colorArray=np.empty((3,0))
    for vector in normaliedTape:
        color=(MAX_COLOR/pdRange)*vector
        color=color.astype(np.int)
        colorArray=np.column_stack((colorArray,color))
    return colorArray

def increasePixelSize(colorArray,pixelWidth,pixelHeight):
    """
    for i in range(colorArray.shape[1]):
        startWidth=pixelWidth*i
        endWidth=startWidth+pixelWidth-1
        startHeight=0
        endHeight=startHeight+pixelHeight-1
        rectangle=magnifiedColorArray[startHeight:endHeight,startWidth:endWidth]
        rectangle=colorArray[:,i]
    """
    columnArray=np.zeros((3,0))
    for i in range(colorArray.shape[1]):
        pixelColor=colorArray[:,i]
        for j in range(pixelWidth):
            columnArray=np.column_stack((columnArray,pixelColor))
    magnifiedColorArray=np.zeros((0,colorArray.shape[1]*pixelWidth))
    #make it taller
    for i in range(pixelHeight):
        magnifiedColorArray=np.row_stack((magnifiedColorArray,columnArray))
    return magnifiedColorArray

            
def tape2PILImage(controlTape,minPd,maxPd):
    controlTape=controlTape.copy()
    PIXEL_WIDTH,PIXEL_HEIGHT=20,10
    normalizedControlTape=normalizeControlTape(controlTape,minPd,maxPd)
    colorArray=""
    colorArray=makeColorArray(normalizedControlTape,minPd,maxPd)
    magnifiedColorArray=increasePixelSize(colorArray,PIXEL_WIDTH,PIXEL_HEIGHT)
    pilImage = Image.fromarray(magnifiedColorArray, 'RGB')
    #pilImage.show()
    return pilImage.copy()
    
        