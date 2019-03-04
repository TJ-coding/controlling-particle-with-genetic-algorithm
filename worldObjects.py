import numpy as np
import object as emObjects

class WorldObjects():
    def __init__(self):
        self.obsticleNamesList=["Point Charge","Wire","Unform Magnetic Field","Plate Charge","Control Plate"]
        startPosition=np.zeros((3,1))
        finishPosition=np.zeros((3,1))
        #initialize wrold
        self.buildWorld={}
        self.simulationWorld={}
        for world in [self.buildWorld,self.simulationWorld]:
            startObject=emObjects.StartPoint(startPosition.copy())
            finishObject=emObjects.FinishPoint(finishPosition.copy())
            world[id(startObject)]=startObject
            world[id(finishObject)]=finishObject