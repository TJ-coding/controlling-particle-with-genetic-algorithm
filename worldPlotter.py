import tkinter
from tkinter import ttk
import matplotlib.backends.tkagg as tkagg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import(FigureCanvasTkAgg, NavigationToolbar2Tk)
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as collections
import emSimulation
import matplotlib.colors as colors
from inputValidation import secondArgValidPoint

class WorldPlotter():
    def __init__(self,figure,objectList):
        self.figure=figure
        self.__initializeAttributes(objectList)
    def __initializeAttributes(self,objectList):
        self.ax=self._addSubPlot()
        self.objectList=objectList
        self.artList={}  
        #plottedObjIdList
        self.objIdList=[]
        #plottedArtIdList
        self.artIdList=[]
        #translate objId to artId
        self.objId2ArtIdDict={}
        #translate artId to objId
        self.artId2ObjIdDict={}
        #translate objId to nodes of previous plot
        self.objId2previousNodesDict={}
        #translate artId to Art object
        self.artId2ArtDict={}
        #flag made true if something have changed after showWorld method was called
        self.worldChanged=False
        self.POINT_TYPE=("Point Charge","Test Charge")
        self.SURFACE_TYPE=("Uniform Magnetic Field","Plate Charge","Start Point",
                      "Finish Point","Positive Enforcement Token",
                      "Negative Enforcement Token")
        
        
    def __showForTheFirstTime(self,obj):
        # first time to plot
        COLOR_BY_TYPE={"Start Point":"green","Finish Point":"orange",
                        "Positive Enforcement Token":"gray",
                        "Negative Enforcement Token":"black"}
        artist=None
        objType=obj.type
        if(objType in self.POINT_TYPE):
            position=obj.getNodes()
            artist=self._plotPoint(position)
        elif(objType in self.SURFACE_TYPE):
            surfaces=obj.getSurfaces()
            #choosing color
            if(objType in COLOR_BY_TYPE):
                color=COLOR_BY_TYPE[objType]
            else:
                #default color
                color="blue"
            artist=self._plotSurfaces(surfaces,color=color)
        #updating dictionaries
        if(artist!=None):
            nodes=obj.getNodes()
            self.__appendNewElementToLists(obj,artist,nodes)
        else:
            print("Have not been told how to plot")
    
    def __updateObjArtist(self,obj):
        objType=obj.type
        previousNodes=self.objId2previousNodesDict[id(obj)]
        currentNodes=obj.getNodes()
        nodesHaveNotChanged=np.array_equal(previousNodes,currentNodes)
        nodesHaveChanged=not nodesHaveNotChanged
        worldChanged=False
        if(nodesHaveChanged):
            #object have changed position therefore update plot
            if(objType in self.POINT_TYPE or objType in self.SURFACE_TYPE):
                if(objType in self.POINT_TYPE):
                    self._updatePoint(id(obj),currentNodes)
                elif(objType in self.SURFACE_TYPE):
                    surfaces=obj.getSurfaces()
                    self._updateSurfaces(id(obj),surfaces)
                #update previous nodes
                self.objId2previousNodesDict[id(obj)]=currentNodes.copy()
                worldChanged=True
            else:
                print("Don't know how to update "+objType)
        else:
            #nothing in build world was updated
            worldChanged=False
        return worldChanged
        
               
    def showWorld(self):
        #this is set to true if something is changed
        self.worldChanged=False
        #plotting every object
        for objId in self.objectList:
            obj=self.objectList[objId]
            if objId not in self.objIdList:
               self.__showForTheFirstTime(obj)
               self.worldChanged=True
            else:
                self.worldChanged=self.__updateObjArtist(obj)
                
    def resetWrold(self,objectList):
        self.ax.remove()
        self.__initializeAttributes(objectList)
    
    def __appendNewElementToLists(self,obj,art,nodes):
        objId=id(obj)
        artId=id(art)
        self.objIdList.append(objId)
        if(type(art)!=list):
            self.artIdList.append(artId)
            self.artId2ObjIdDict[artId]=objId

        else:
            print("its a list")
            for a in art:
                self.artIdList.append(id(a))
                #2 to 1 relation
                self.artId2ObjIdDict[id(a)]=objId

        self.objId2ArtIdDict[objId]=artId
        self.objId2previousNodesDict[objId]=nodes.copy()
        self.artId2ArtDict[artId]=art
                    
    def _plotPoint(node):
        pass
    def _updatePoint(objId,node):
        pass
    def _plotSurfaces(self,surfaces,color="blue"):
        pass
    def _updateSurefaces(objId,surfaces):
        pass
 
class WorldPlotter3d(WorldPlotter):
    def __init__(self,figure,objectList):
        super().__init__(figure,objectList)
        self.quiversField=None
        self.quiversFieldType=None
        self.emField=emSimulation.EMSimulation(self.objectList)
        
        #make new quiver field
        startPoint=2
        endPoint=-2
        #keep this value low since it will make it lag (O(n^3))
        pixelNumber=5
        xLine=np.linspace(startPoint,endPoint,num=pixelNumber)
        yLine=xLine.copy()
        zLine=xLine.copy()
        #Return coordinate matrices from coordinate vectors.
        x,y,z= np.meshgrid(xLine,yLine,zLine)
        x1d,y1d,z1d=x.flatten(),y.flatten(),z.flatten()
        self.vectorFieldPoints=[x1d,y1d,z1d]
    
    #overrifing show plot to plot quiver field as well
    def showWorld(self):
        super().showWorld()
        #plotting vector field (try to minimize doing this since it cause lag)
        if(self.quiversFieldType!=None and self.worldChanged==True):
            fieldType=self.quiversFieldType
            self.__replotVectorField(fieldType)
    
    #must be called after setting up figure canvas to allow 3d rotation (only works in 3d)
    def enableMouseRotation(self):
        self.ax.mouse_init()
    #only works in 3d
    def setCameraAngle(self,phi,theta):
        self.ax.view_init(phi, theta)
    
    ###overriding methods#######################################################
    def _addSubPlot(self):
        return self.figure.add_subplot(111,projection="3d")
            
    
    def _plotPoint(self,node):
        x,y,z=node[0,0],node[1,0],node[2,0]
        print(x,y,z)
        return self.ax.plot([x],[y],[z], marker='o',picker=5)[0]
        
    def _updatePoint(self,objId,node):
        x,y,z=node[0],node[1],node[2]
        #finding artist of the boject
        artId=self.objId2ArtIdDict[objId]
        artist=self.artId2ArtDict[artId]
        #updating the artist
        artist.set_data(np.array([x,y]))
        artist.set_3d_properties(z, 'z')
            
    def _plotSurfaces(self,surfaces,color="blue"):
        polygon=Poly3DCollection(surfaces,color=color)
        self.ax.add_collection3d(polygon)
        return polygon
    
    def _updateSurfaces(self,objId,surfaces):
        #finding artist of the boject
        artId=self.objId2ArtIdDict[objId]
        artist=self.artId2ArtDict[artId]
        artist.set_verts(surfaces)
        
    def _plotPlateCharge(self):
        pass
    
    
    def __findVectorComponents(self,fieldType,xPoints,yPoints,zPoints):
        iComponents,jComponents,kComponents=[],[],[]
        for n in range(len(xPoints)):
            xPoint,yPoint,zPoint=xPoints[n],yPoints[n],zPoints[n]
            position=np.array([xPoint,yPoint,zPoint],dtype=np.float).reshape((3,1))
            if (fieldType=="E"):
                vectI,vectJ,vectK=self.emField.findObsticlesEField(position)
                #they are negative to make positive go to negative arrow
                vectI*=-1
                vectJ*=-1
                vectK*=-1
            elif (fieldType=="B"):
                vectI,vectJ,vectK=self.emField.findObsticlesBField(position)
            iComponents.append(vectI[0])
            jComponents.append(vectJ[0])
            kComponents.append(vectK[0])
        return iComponents,jComponents,kComponents
    
    #plot new vector field
    def __replotVectorField(self,fieldType):
        #remove quiver field
        if(self.quiversField!=None):
            #get rid of previous quiver field
            self.quiversField.remove()
        if(fieldType!=None):
            xPoints=self.vectorFieldPoints[0]
            yPoints=self.vectorFieldPoints[1]
            zPoints=self.vectorFieldPoints[2]
            #segments contain list required to plot vector field
            iComponents,jComponents,kComponents=self.__findVectorComponents(fieldType,xPoints,yPoints,zPoints)
            #plot new quiver field
            self.quiversField=self.ax.quiver(xPoints,yPoints,zPoints,iComponents,jComponents,kComponents,length=0.35,normalize=True)
        else:
            #no field selected
            self.quiversField=None
        self.quiversFieldType=fieldType
    
    #FieldType is either None E or B
    def changeVectorFieldType(self,fieldType):
        self.quiversFieldType=fieldType
        self.__replotVectorField(fieldType)
        

#this method of _updateVectorField is more optimal but do not provide arrow tails and must be normalized manually
"""
    def _updateVectorField(self):
        x1d=self.vectorFieldPoints[0]
        y1d=self.vectorFieldPoints[1]
        z1d=self.vectorFieldPoints[2]
        segments=[]

        for n in range(len(x1d)):
            position=[x1d[n],y1d[n],z1d[n]]
            if (self.quiversFieldType=="E"):
                u,v,w=self.emField.findEField(position)
                u*=10**9
                v*=10**9
                w*=10**9
            elif (self.quiversFieldType=="B"):
                u,v,w=self.emField.findBField(position)
            segments.append([[position[0],position[1],position[2]],[position[0]+u[0],position[1]+v[0],position[2]+w[0]]])


        self.quiversField.set_segments(segments)

"""    
class WorldPlotter2d(WorldPlotter):
    def __init__(self,figure,objectList,plane=("x","y")):
        super().__init__(figure,objectList)
        self.plane=plane        

    def __flatNodes(self,node):
        #convert them into 2dimentional array
        if(len(node.shape)==1):
            node=np.array([[node[0]],[node[1]],[node[2]]])

        #substitute x and y coordinate by defined coordinate

        subICoord=["x","y","z"].index(self.plane[0])
        subJCoord=["x","y","z"].index(self.plane[1])
        #make an operator to extract wanted component of node
        iFilterOperator=np.array([[0,0,0],[0,0,0],[0,0,0]])
        iFilterOperator[0][subICoord]=1
        jFilterOperator=np.array([[0,0,0],[0,0,0],[0,0,0]])
        jFilterOperator[1][subJCoord]=1
        ijFilterOperator=iFilterOperator+jFilterOperator 
        
        #apply the operator
        filtedMatrix=np.dot(ijFilterOperator,node)
        #resize from 3d matrix to 2 d matrix
        filtedMatrix=filtedMatrix[:-1,:]
        
        return filtedMatrix
    
    ###overriding methods#######################################################
    def _addSubPlot(self):
        ax=self.figure.add_subplot(111)
        ax.set_xlim([-2,2])
        ax.set_ylim([-2,2])
        return ax
    
    def _plotPoint(self,node):
        node=self.__flatNodes(node)
        plottedArtist= self.ax.plot([node[0]],[node[1]], marker='o',picker=5)[0]
        return plottedArtist
    
    def _updatePoint(self,objId,node):
        node=self.__flatNodes(node)
        #finding artist of the boject
        artId=self.objId2ArtIdDict[objId]
        artist=self.artId2ArtDict[artId]
        #updating the artist
        artist.set_data(np.array([node[0],node[1]]))
    
    def _plotSurfaces(self,surfaces,color="blue"):
        artistList=[]
        for surface3d in surfaces:
            surface2d=np.empty([2,0])
            #flattining nodes
            for node in surface3d:
                #convert list representation of node to array form of representation
                node=np.array(node)


                flatNode=self.__flatNodes(node)
                surface2d=np.column_stack((surface2d,flatNode))
            x=surface2d[0,:]
            y=surface2d[1,:]
            patch=patches.Polygon(xy=list(zip(x,y)),ls='-',lw=3,picker=5,color=color)
            artist=self.ax.add_patch(patch)
            artistList.append(artist)
        
        return artistList
    
    def _updateSurfaces(self,objId,surfaces):
        #finding artist of the boject
        artId=self.objId2ArtIdDict[objId]
        patchList=self.artId2ArtDict[artId]
        print("UPDATE SURFACE 2d")

        
        for n in range(len(surfaces)):
            surface3d=surfaces[n]
            surfaceArtist=patchList[n]
            #flatten node
            surface2d=np.empty([2,0])
            for node in surface3d:
                node=np.array(node)
                flatNode=self.__flatNodes(node).copy()
                surface2d=np.column_stack((surface2d,flatNode))
            x=surface2d[0,:]
            y=surface2d[1,:] 

            #updateSurface
            surfaceArtist.set_xy(list(zip(x,y)))
