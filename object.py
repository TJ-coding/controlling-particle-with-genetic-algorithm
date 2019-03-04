import numpy as np
import math
import worldConstants
import pandas as pd
import matplotlib.pyplot as plt

from inputValidation import (firstArgValidPoint,secondArgValidPoint)


class MathToolBox():
    def __init__(self):
        pass
            
    #point must be 3 dimentional
    @staticmethod
    @firstArgValidPoint
    @secondArgValidPoint
    def _distanceToPoint(point1,point2):
        dr=point1-point2
        drSquare=np.square(dr)
        distance=math.sqrt(drSquare[0]+drSquare[1]+drSquare[2])
        return distance
    #does not take in count of boundary of line
    #arc=ndarray([[p1x,p2x][p1z,p2z][p1z,p2z]])
    "p1*-------*p2"
    #where p1 and p2 are the edge points of line
    @staticmethod
    def _distanceToLine(point,arc):
        lineVector=arc[:,1]-arc[:,0]
        #project point on the lineVector
        projectedPoint=np.dot(lineVector,arc)
        #vector between point and projected point
        d=projectedPoint-point
        #distance of the d vector
        distance=np.linalg.norm(d)
        return distance
    """
    @staticmethod
    def _distanceToSurface(point,surface):
        return distance
    """
    #boundingBoxCollision
    #representation of bounding box
    """
              *p7
             /  \
            /    \
         p8*\    /*p6
           | \  / |
           |  \/  |
         p4*  *p5 *p2
            \ |  /
             \| /
              *p1
    boundingBox=ndarray([[p1x,p2x,p3x,p4x,p5x,p6x,p7x,p8x],
    [p1y,p2y,p3y,p4y,p5y,p6y,p7y,p8y],
    [p1z,p2z,p3z,p4z,p5z,p6z,p7z,p8z],
    ])"""
    #projection representation
    """
             /*point    
            / |
     p1*   /  |     *p2
       |  /   |     |
       *_/____*_____*_____<-line to project on 
       pA    pD     pB
    """
    #this method that implement SAT only work with box 
    #(because of the way in whcih it extract surface from box)
    """
    @staticmethod
    @firstArgValidPoint
    
    def boundingBoxCollision(point, boundingBox):
        p1=boundingBox[:,0]
        p2=boundingBox[:,1]
        p4=boundingBox[:,3]
        p5=boundingBox[:,4]
        
        #lines to project point on to
        arcsToProjectOn=[[p1,p2],[p1,p4],[p1,p5]]
        
        #projecting point to lines
        isColliding=True
        for arc in arcsToProjectOn:
            vectLine=arc[0]-arc[1]
            norm=np.linalg.norm(vectLine)
            pA=np.dot(vectLine,arc[0])/norm
            pB=np.dot(vectLine,arc[1])/norm
            pD=np.dot(vectLine,point)/norm
            if(pD>max([pA,pB]) or pD<min([pA,pB])):
                isColliding=False
                break
        return isColliding
    """
    @staticmethod
    @firstArgValidPoint
    def boundingBoxCollision(point, boundingBox):
        p1=boundingBox[:,0]
        p2=boundingBox[:,1]
        p4=boundingBox[:,3]
        p5=boundingBox[:,4]
        #lines to project point to
        arcsToProjectOn=[[p1,p2],[p1,p4],[p1,p5]]
        
        #projecting point to lines
        isColliding=True
        for arc in arcsToProjectOn:
            vectLine=arc[1]-arc[0]
            norm=np.linalg.norm(vectLine)
            pA=np.dot(vectLine,arc[0])/norm
            pB=np.dot(vectLine,arc[1])/norm
            pL=np.dot(vectLine,point)/norm
            if(pL>max([pA,pB]) or pL<min([pA,pB])):
                isColliding=False
        return isColliding

    #angles in radians
    #rotates around origin
    @staticmethod
    @firstArgValidPoint
    @secondArgValidPoint
    def _rotateMatrix(origin,angles,node):
        angleX=angles[0]
        angleY=angles[1]
        angleZ=angles[2]
        #define rotation matrix
        rotateAboutX=np.array([
                [1,0,0],
                [0,math.cos(angleX),-math.sin(angleX)],
                [0,math.sin(angleX),math.cos(angleX)]
                ])
        rotateAboutY=np.array([
                [math.cos(angleY),0,math.sin(angleY)],
                [0,1,0],
                [-math.sin(angleY),0,math.cos(angleY)]
                ])
        rotateAboutZ=np.array([
                [math.cos(angleZ),-math.sin(angleZ),0],
                [math.sin(angleZ),math.cos(angleZ),0],
                [0,0,1]
                ])
        #apply rotation matrix
        centeredNodes=node-origin
        rotatedStructure=centeredNodes
        for rotationMatrix in [rotateAboutX,rotateAboutY,rotateAboutZ]:    
            rotatedStructure=np.dot(rotationMatrix,rotatedStructure)
        #remove centering (move back to original position)
        rotatedStructure=rotatedStructure+origin
        return rotatedStructure

    @staticmethod
    def _makeCuboid(x,y,z):
        #making bottom plate
        p1=[[0],[0],[0]]
        p2=[[x],[0],[0]]
        p3=[[x],[y],[0]]
        p4=[[0],[y],[0]]
        bottomPlateNodes=[np.array(pointList) for pointList in[p1,p2,p3,p4]]
        #making top plate
        topPlateNodes=[]
        separationVector=np.array([[0],[0],[z]])
        for node in bottomPlateNodes:
            topPlateNodes.append(node+separationVector)  
        #convert them to numpy array
        nodeList=bottomPlateNodes+topPlateNodes
        print("test-------------")
        xs=[node[0][0] for node in nodeList ]
        print(xs)
        ys=[node[1][0] for node in nodeList ]
        zs=[node[2][0]for node in nodeList ]
        cuboid=np.array([xs,ys,zs])
        print(cuboid.shape)
        return cuboid
 

class Object(MathToolBox):

    @secondArgValidPoint
    def __init__(self,position,orientation):
        self.position=position
        self.orientation=np.array([[0],[0],[0]])
        self.type=""
        self.worldConstants=worldConstants.WorldConstants()
    def getNodes(self):
        return self.position
    def translatePosition(self,translationVector):
        pass
    @secondArgValidPoint
    def translatePosition(self,translationVector):
        translationVector=translationVector.copy()
        print(self.position)
        self.position+=translationVector
        
class TestCharge(Object):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.zeros((3,1)),charge=1,mass=1):
        super().__init__(position,orientation)
        self.type="Test Charge"
        self.charge=charge
        self.mass=mass
        self.position=position
        
    def getNodes(self):
        
        return self.position
    
    def getEField(self,position):
        return np.zeros((3,1))
    def getBField(self,position):
        return np.zeros((3,1))
    
class Obsticle(Object):
    def __init__(self):
        self.editableParams={}
    pass
    def getEField(self,position):
        pass
    def getBField(self,position):
        pass
    
class PointCharge(Object):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),charge=-1.6):
        super().__init__(position,orientation)
        self.charge=charge
        self.orientation=orientation
        self.type="Point Charge"
    def getNodes(self):
        return self.position.copy()
    
    @secondArgValidPoint
    def getEField(self,point):
        #finding normalised direction vector from point to the particle
        directionToPoint=self.position-point
        origin=np.zeros((3,1),dtype=np.float)
        directonVectorLength=self._distanceToPoint(origin,directionToPoint)
        normalisedDirectionVector=directionToPoint/directonVectorLength
        
        r=self._distanceToPoint(self.position,point)
        q=self.charge
        k=self.worldConstants.coulombConstant
        if(r!=0):
            E=(k*q)/(r**2)
            E=E*normalisedDirectionVector
        else:
            #E is infinite set it to 0
            E=np.array([[0],[0],[0]])
        return E
    
    @secondArgValidPoint
    def getBField(self,point):
        return 0
    @secondArgValidPoint
    def translatePosition(self,translationVector):
        print("translation")
        translationVector=translationVector.copy()
        self.position+=translationVector
class Wire(Object):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),curren=1,length=1):
        self.current=1
        self.length=1
        px,py,pz=position[0],position[1],position[2]
        self.nodes=[[px,px],[py,py],[pz,pz+length]]

    def getNodes(self):
        return self._rotateMatrix(origin,angles,node)
    def getEField(self,point):
        return 0
    def getBField(self,point):
        myu=self.worldConstants.magneticPermiability
        I=self.current
        r=self.distanceToLine(point,self.nodes)
        B=(myu*I)/(2*math.pi*r)
        return B
    
class UniformField(Object):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]])):
        super().__init__(position,orientation)
        self._plateSeparataion=1
        self.plateDimension=[1,1]
        self.E=0
        self.B=0
        
        self.structure=self._makeCuboid(self.plateDimension[0],
                                   self.plateDimension[1],self._plateSeparataion)
        
        """
        self.nodes=np.ndarray([3,0])
        for aNode in nodeList:
            np.column_stack((self.nodes,aNode))
            print(pd.DataFrame(self.nodes))"""
    
    #nodes returned here have position and rotation applied to the structure
    def getNodes(self):
        #translate structure according to position
        nodes=self.position+self.structure
        #rotate the nodes according to orientation
        #origin have shape (3,) convert to (3,1)
        aPoint=nodes[:,0].copy()
        rotationOrigin=np.array([[aPoint[0]],[aPoint[1]],[aPoint[2]]])
        rotatedNode=self._rotateMatrix(rotationOrigin,self.orientation,nodes)
        return rotatedNode
    
    def getSurfaces(self):
        nodes=self.getNodes()

        topPlate=[nodes[:,4].tolist(),nodes[:,5].tolist(),nodes[:,6].tolist(),nodes[:,7].tolist()]
        bottomPlate=[nodes[:,0].tolist(),nodes[:,1].tolist(),nodes[:,2].tolist(),nodes[:,3].tolist()]

        return [topPlate,bottomPlate]

    def translatePosition(self,translationVector):
        print("TRANSLATION VECTOR")
        translationVector=translationVector.copy()
        self.position+=translationVector
        
    def getEField(self,point):
        boundingBox=self.getNodes()
        isColliding=self.boundingBoxCollision(point,boundingBox)
        if(isColliding):
            E=self.E
        else:
            E=0
        orientation=np.array([0,0,1]).reshape((3,1))
        aPoint=self.getNodes()[:,0].copy()
        origin=np.array([[aPoint[0]],[aPoint[1]],[aPoint[2]]])
        rotatedOrientation=self._rotateMatrix(origin,self.orientation,orientation)
        return E*rotatedOrientation
    
    def getBField(self,point):
        boundingBox=self.getNodes()
        isColliding=self.boundingBoxCollision(point,boundingBox)
        if(isColliding):
            B=self.B
        else:
            B=0
        orientation=np.array([0,0,1]).reshape((3,1))
        aPoint=self.getNodes()[:,0].copy()
        origin=np.array([[aPoint[0]],[aPoint[1]],[aPoint[2]]])
        rotatedOrientation=self._rotateMatrix(origin,self.orientation,orientation)
        return B*rotatedOrientation

class UniformMagneticField(UniformField):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),B=1):
        super().__init__(position,orientation)
        self.B=np.array([[0],[0],[B]])
        self.E=np.zeros([3,1])
        self.type="Uniform Magnetic Field"
    
class UniformElectricField(UniformField):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),E=1):
        super().__init__(position,orientation,E)
        self.B=np.zeros([3,1])
        self.E=np.array([[0],[0],[E]])
        self.type="Uniform Electric Field"

class PlateCharge(UniformField):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),pd=1):
        super().__init__(position,orientation)
        self.type="Plate Charge"
        self.pd=pd
    
    @property
    def pd(self):
        return self._pd
    #pd setter updates the E field as well
    @pd.setter
    def pd(self,pd):
        self._pd=pd
        self.E=pd/self._plateSeparataion

class ControlPlate(PlateCharge):
    @secondArgValidPoint
    def __init__(self,position,orientation,dtStep,controlTape=[]):
        super().__init__(position,orientation=orientation,pd=0)
        self.type="Control Plate"
        self.orientation=orientation
        self.controlTape=controlTape
        self.__dtStep=dtStep
        
    def getEField(self,point,time):
        controlTapeIndex=int(time/self.__dtStep)
        if(controlTapeIndex>len(self.controlTape)-1):
            raise ValueError("%s is outside time covered by the controlTape" % time)
            E=None
        else:
            self.pd=self.controlTape[controlTapeIndex]
            #E gets set by pd setter
            #E=super().getEField(point)
            orientation=np.array([0,0,1]).reshape((3,1))
            aPoint=self.getNodes()[:,0].copy()
            origin=np.array([[aPoint[0]],[aPoint[1]],[aPoint[2]]])
            rotatedOrientation=self._rotateMatrix(origin,self.orientation,orientation)
        return self.E*rotatedOrientation
            
        
    @property
    def controlTape(self):
        return self._controlTape
    
    @controlTape.setter
    def controlTape(self,controlTape):
        self._controlTape=controlTape
        
        
class Token(Object):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]]),cubeSize=[0.1,0.1,0.1]):
        super().__init__(position,orientation)
        self.type="Token"
        self.structure=self._makeCuboid(cubeSize[0],cubeSize[1],cubeSize[2])
        
    #nodes returned here have position and rotation applied to the structure
    @property
    def nodes(self):
        nodes=self.position+self.structure
        #print(pd.DataFrame(nodes))
        #rotate the nodes according to orientation
        #origin have shape (3,) convert to (3,1)
        rotationOrigin=nodes[:,0].copy()
        rotationOrigin=rotationOrigin.reshape((3,1))
        rotatedNode=self._rotateMatrix(rotationOrigin,self.orientation,nodes)
        return rotatedNode
    
    def getSurfaces(self):
        nodes=self.nodes
        nodeColumnNum=nodes.shape[1]
        #converting nodes into list
        nodesAsList = [nodes[:,c].tolist() for c in range(nodeColumnNum)]
        
        topSideIndex=[4,5,6,7]
        bottomSideIndex=[0,1,2,3]
        leftSideIndex=[0,3,7,4]
        rightSideIndex=[0,3,7,4]
        frontSideIndex=[0,1,5,4]
        backSideIndex=[3,2,6,7]
        
        allSidesIndex=[topSideIndex,bottomSideIndex,
                       leftSideIndex,rightSideIndex,frontSideIndex,backSideIndex]
        allSidesNodes=[]
        for sideIndex in allSidesIndex:
            thisSideNodes=[]
            for index in sideIndex:
                aNodeInList=nodesAsList[index]
                thisSideNodes.append(aNodeInList)
            allSidesNodes.append(thisSideNodes)
        return allSidesNodes
    
    def isColliding(self,position):
        boundingBox=self.nodes
        return self.boundingBoxCollision(position,boundingBox)
    
        
class StartPoint(Token):
    @secondArgValidPoint
    def __init__(self,position):
        super().__init__(position)
        self.type="Start Point"

class FinishPoint(Token):
    @secondArgValidPoint
    def __init__(self,position):
        super().__init__(position)
        self.type="Finish Point"


class EnforcementToken(Token):
    @secondArgValidPoint
    def __init__(self,position,orientation=np.array([[0,0,0]])):
        super().__init__(position,orientation)
        self.type="Enforcement Token"

class PositiveEnforcementToken(EnforcementToken):
    def __init__(self,position):
        super().__init__(position)
        self.type="Positive Enforcement Token"
        self.haveCollidedBefore=False

    #can only collide once since specie might continuously collect same token
    def isColliding(self,position):
        isColliding=False
        if(self.haveCollidedBefore==False):
            boundingBox=self.nodes
            isColliding=self.boundingBoxCollision(position,boundingBox)
            if(isColliding):
                self.haveCollidedBefore=True
        return isColliding
    
    def collistionReset(self):
        self.haveCollidedBefore=False
        
class NegativeEnforcementToken(EnforcementToken):
    def __init__(self,position):
        super().__init__(position)
        self.type="Negative Enforcement Token"
       
        

    