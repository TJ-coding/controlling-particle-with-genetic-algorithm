import numpy as np
import object as emObjects
import math
from inputValidation import secondArgValidPoint
class secondODESolver():
    def __init__(self,dtStep,initialPosition=np.array([[0],[0],[0]]),initialVelocity=np.array([[0],[0],[0]])):
        self.positionOverTime=[initialPosition]
        print("POSITION INITIALIZED INITIALIZED-----------------------")
        print(self.positionOverTime)
        self.velocityOverTime=[initialVelocity]

        self._dtStep=dtStep

    def reset(self,initialPosition=np.array([[0],[0],[0]]),initialVelocity=np.array([[0],[0],[0]])):
        self.positionOverTime=[initialPosition]
        self.velocityOverTime=[initialVelocity]

    #this implementation can only calculate 2nd order differential equation
    def rungeKutterMethod(self, maxValue):

        dt=self._dtStep
        t=0

        for i in range(int(maxValue/dt)):
            t=i*dt
            previousVelocity=self.velocityOverTime[-1]
            previousPosition=self.positionOverTime[-1]
            #K represent change in velocity at various points in time
            k1=dt*self.acceleration(t,previousPosition,previousVelocity)
            #finding k2
            t=t+dt/2
            position=previousPosition+k1*(dt/2)
            velocity=previousVelocity+(k1/2)
            k2=dt*self.acceleration(t,position*(dt/2),velocity)
            #finding k3
            t=t+dt/2
            position=previousPosition+k2*(dt/2)
            velocity=previousVelocity+(k2/2)
            k3=dt*self.acceleration(t+dt/2,position,velocity)
            #finding k4
            t=t+dt
            position=previousPosition+k3*dt
            velocity=previousVelocity+k3
            k4=dt*self.acceleration(t+dt,position,velocity)
            #weigh, sum and average various
            k=(k1+2*k2+2*k3+k4)/6
            #velocity
            velocity=previousVelocity+k

            #calculate lower order derrivitives from velocity
            previousPosition=self.positionOverTime[-1]
            previousSolutions=[None,previousPosition,previousVelocity]
            derrivitiveOrderNumber=len(previousSolutions)
            thisSolution=[None,None,velocity]
            #calculates position from velocity since the order calculating from is 2nd order
            #This does not need to be a loop since it itterate only once but it is needed
            #if differential equation of higher order needs to be calculated
            for order in range(derrivitiveOrderNumber-2,0,-1):
                thisSolution[order]=previousSolutions[order]+(thisSolution[order+1]*self._dtStep)

            self.positionOverTime.append(thisSolution[1])
            self.velocityOverTime.append(thisSolution[2])

    #require previousVlaues attributes to be set
    def acceleration(self,t,previousVelocity):
        pass
        # return vector

class EMSimulation():
    #kwargs used for multiple inheritance by EMControlledChamber
    def __init__(self,worldObject,**kwargs):
        self.worldObject=worldObject
        self._dtStep=0.1
        #must be declared after plates are defined
        self.controlTape=[np.zeros((3,1))]
        #find start position for test charge
        self._startPointObj=self._findStartObj(worldObject)
        self._finishPointObj=self._findFinishObj(worldObject)
        self._posTokenList=self._findTypeOfObjs(worldObject,
                                                   "Positive Enforcement Token")
        self._negTokenList=self._findTypeOfObjs(worldObject,
                                                   "Negative Enforcement Token")



    @staticmethod
    def _findTypeOfObjs(worldObject,objType):
        #startToken is not in worldObjects
        foundObjs=[]

        for objId in worldObject:
            obj=worldObject[objId]
            if(obj.type == objType):
                foundObjs.append(obj)
        return foundObjs

    def _findStartObj(self,worldObject):
        startPoint=self._findTypeOfObjs(worldObject,"Start Point")[0]
        if(startPoint==[]):
            #startToken is not in worldObjects
            raise ValueError("worldObject used by EMSimulation must contain a StartPoint object")
        return startPoint

    def _findFinishObj(self,worldObject):
        startPoint=self._findTypeOfObjs(worldObject,"Finish Point")[0]
        if(startPoint==[]):
            #startToken is not in worldObjects
            raise ValueError("worldObject used by EMSimulation must contain a FinishPoint object")
        return startPoint


    #find fields contributed by obsticles
    @secondArgValidPoint
    def findObsticlesEField(self,position):
        E=np.array([[0],[0],[0]],dtype="float")
        for objId in self.worldObject:
            obj=self.worldObject[objId]
            if(obj.type not in ("Start Point", "Finish Point","Positive Enforcement Token","Negative Enforcement Token")):
                E+=obj.getEField(position)

        return E

    def findObsticlesBField(self,position):
        B=np.array([[0],[0],[0]],dtype="float")
        for objId in self.worldObject:
            obj=self.worldObject[objId]
            if(obj.type not in ("Start Point", "Finish Point","Positive Enforcement Token","Negative Enforcement Token")):
                B+=obj.getBField(position)
        return B

    def resetWorldObject(self,worldObject):
        self.worldObject=worldObject



class EMControlledChamber(EMSimulation,secondODESolver):
    def __init__(self,worldObject,dtStep=0.1):
        self._dtStep=dtStep
        dtStep=self._dtStep
        self.xPlate,self.yPlate,self.zPlate=self.__makeControlPlates(self._dtStep)
        EMSimulation.__init__(self,worldObject)
        secondODESolver.__init__(self,dtStep)
        self.reset()

    #controlPlateSize is the length of a side of the cube
    @staticmethod
    def __makeControlPlates(dtStep,controlPlateSize=2):
        position=np.array([[-controlPlateSize/2],
                           [-controlPlateSize/2],[-controlPlateSize/2]])

        xOrientation=np.array([[0],[math.pi/2],[0]])
        yOrientation=np.array([[math.pi/2],[0],[0]])
        zOrientation=np.array([[0],[0],[0]])

        controlPlateX=emObjects.ControlPlate(position,xOrientation,dtStep)
        controlPlateY=emObjects.ControlPlate(position,yOrientation,dtStep)
        controlPlateZ=emObjects.ControlPlate(position,zOrientation,dtStep)
        return controlPlateX, controlPlateY, controlPlateZ

    def findControlledE(self,position,time):
        controlledE=np.zeros((3,1),dtype=np.float)
        for controlPlate in [self.xPlate,self.yPlate,self.zPlate]:
            controlledE+=controlPlate.getEField(position,time)
        return controlledE

    def findEMField(self,position,time):
        controlledE=self.findControlledE(position,time)
        obsticleE=self.findObsticlesEField(position)

        obsticleB=self.findObsticlesBField(position)
        netE=controlledE+obsticleE
        netB=obsticleB
        """
        print("obsticleE")
        print(obsticleE)
        print("netE")
        print(netE)
        print("controlledE")
        print(controlledE)
        """
        return netE, netB

    def runSimulation(self,maxTime):
        self.rungeKutterMethod(maxTime)


    #return numbers collected
    def __numOfPosTokenCollection(self,position):
        numOfCollection=0
        for posToken in self._posTokenList:
            isColliding=posToken.isColliding(position)
            if(isColliding):
                numOfCollection+=1
        return numOfCollection

    def __resetPosTokens(self):
        for posToken in self._posTokenList:
            posToken.collistionReset()


    #return numbers collided
    def __numOfNegTokenCollistion(self,position):
        numOfCollision=0
        for negToken in self._negTokenList:
            isColliding=negToken.isColliding(position)
            if(isColliding):
                numOfCollision+=1
        return numOfCollision


    def getResults(self):
        finishPointReached=False
        posEnforcementCollected=0
        negEnforcementCollected=0
        for position in self.positionOverTime:
            #if finish point is reached
            if(self._finishPointObj.isColliding(position)==True):
                finishPointReached=True
                print("FINISH REACHED")
                self.__resetPosTokens()
                break
            else:
                posEnforcementCollected+=self.__numOfPosTokenCollection(position)
                negEnforcementCollected+=self.__numOfNegTokenCollistion(position)
        self.__resetPosTokens()
        result={}
        result["numOfPosTokensCollected"]=posEnforcementCollected
        result["numOfNegTokensCollected"]=negEnforcementCollected
        result["goalReached"]=finishPointReached
        return result

    def reset(self):
        self._startPointObj=self._findStartObj(self.worldObject)
        self._startPointObj=self._startPointObj.position
        self._finishPointObj=self._findFinishObj(self.worldObject)
        self._posTokenList=self._findTypeOfObjs(self.worldObject,
                                                   "Positive Enforcement Token")
        self._negTokenList=self._findTypeOfObjs(self.worldObject,
                                                   "Negative Enforcement Token")
        super().reset(initialPosition=self._startPointObj)

    #overriding method
    def acceleration(self,time,position,velocity):
        #property of point charge
        q = 1 # Charge
        m=2
        E,B=self.findEMField(position,time)

        #convert everything to (3,) since cross product can not take (3,1)
        F= q*(E.reshape(3,)+np.cross(velocity.reshape(3,),B.reshape(3,)))
        F=F.reshape(3,1)

        a=F/m

        return a

    @property
    def controlTape(self):
        return self._controlTape

    @controlTape.setter
    def controlTape(self,controlTape):
        if(type(controlTape)==list):
            xTape=[vector[0,0]for vector in controlTape]
            yTape=[vector[1,0]for vector in controlTape]
            zTape=[vector[2,0]for vector in controlTape]
            self._controlTape=controlTape
            self.xPlate.controlTape=xTape
            self.yPlate.controlTape=yTape
            self.zPlate.controlTape=zTape
        else:
            raise ValueError("controlTape must be a list that contain (3,1) numpy arrays %s"%str(type(controlTape)))
