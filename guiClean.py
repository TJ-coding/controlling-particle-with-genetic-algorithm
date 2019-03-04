import tkinter
from tkinter import ttk


import matplotlib.backends.tkagg as tkagg

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import(FigureCanvasTkAgg, NavigationToolbar2Tk)
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import pandas as pd

import object as emObjects
import worldPlotter
import evolution
import tape2PIL
import copy
from PIL import ImageTk
from PIL import Image
import emSimulation    
import time

class Window():
    def __init__(self):
        self.width=0
        self.height=0
    def update(self):
        pass

class MainWindow(Window):
    def __init__(self, worldConstants,worldObjects):
        super().__init__
        #initialising attributes
        self.width=1400
        self.height=800
        self.constants = worldConstants
        self.worldObjects = worldObjects
        simulationTabFrameName="simulation"
        builderTabFrameName="enviroment builder"
        self.tabFrames={simulationTabFrameName:None,builderTabFrameName:None}
        self.noteBook = None
        self.window = None
        #precedure for initial set ups        
        self.__setUpTKWindow()
        self.__setUpTabs()
        
        #instantiating corresponding tab class
        self.simulationTab=SimulationTab(self,simulationTabFrameName)
        self.builderTab=BuilderTab(self,builderTabFrameName)

    def __setUpTKWindow(self):
        #add window
        print("tk start")
        self.window = tkinter.Tk()
        print("tk root initialize")
        #set window title
        self.window.title("EM simulator")
        #set window size
        self.window.attributes('-fullscreen', False)
        self.window.geometry(str(self.width)+"x"+str(self.height))
        print("tk initialize done tab set up coming up")
        self.__setUpTabs()
        print("tab setup done")
    def __setUpTabs(self):
        #creating a notebook to display frames as tab        
        self.noteBook = tkinter.ttk.Notebook(self.window)
        self.noteBook.grid(row=1,column=0,columnspan=40,rowspan=39)
        #adding a frame to window to group widgets (acts as a tab page)
        for name in self.tabFrames:
            self.tabFrames[name]=ttk.Frame(self.noteBook)
            #add frame to the note book
            self.noteBook.add(self.tabFrames[name],text=name)
                
    def update(self):
        self.window.update_idletasks()
        self.window.update()
        #self.simulationTab.update()

class Tab(Window):
    def __init__(self,mainWindow,frameName):
        self.frameName=frameName
        self.mainWindow=mainWindow
        self.frame=mainWindow.tabFrames[frameName]
        self.worldObjects=mainWindow.worldObjects
    
    @staticmethod
    def _makeListBox(frame,itemNamesList,height=False,scrollBar=False):
        #setting up list menu
        if(height==False):
            listBoxHeight=len(itemNamesList)
        else:
            listBoxHeight=height
        if(scrollBar):
            scrollbar = tkinter.Scrollbar(frame, orient="vertical")
            listBox = tkinter.Listbox(frame, height=listBoxHeight,yscrollcommand=scrollbar.set)
        else:
            listBox = tkinter.Listbox(frame, height=listBoxHeight)
            #tkinter.END specify to insert item at the end
        for itemName in itemNamesList:
            listBox.insert(tkinter.END, itemName)
        #select 0 by default
        listBox.selection_set(first=0)
        return listBox

    def _setUpWorldPlotter3d(self,figure,world):
        worldPlotter3d=worldPlotter.WorldPlotter3d(figure,world)
        worldPlotter3d.enableMouseRotation()
        return worldPlotter3d
    
    def _setUpWroldPlotter2d(self,figure,world,plane):
        worldPlotter2d=worldPlotter.WorldPlotter2d(figure,world,plane)
        return worldPlotter2d
        
        
#deals with everything to do with simulation tab require window class as param
class SimulationTab(Tab):
    def __init__(self,mainWindow,frameName):
        super().__init__(mainWindow,frameName)
        #this initial world ususally contain startPoint and finishPoint Objects
        self.simulationWorld=self.worldObjects.simulationWorld
        self.evolutionChamber=evolution.evolutionChamber(self.simulationWorld)
        self.generationNames=[]
        self._nextGenIndex=0
        self.specieOnDisplay=[]
        self.MAX_PD=1
        self.MIN_PD=-1
        self.TAPE_IMAGE_SIZE=(100,10)
        self.testCharge=emObjects.TestCharge(np.zeros((3,1)))
        self.simulationWorld[id(self.testCharge)]=self.testCharge
        self.__setUpSimulationChamber()
        self.__setUpWidgets()

    def __setUpWidgets(self):
        #self.__setUpWorldDisplay()
        self.__setUpFigure()
        self.worldPlotter=self._setUpWorldPlotter3d(self.figure,self.simulationWorld)
        self.update()
        self.__setUpButtons()
        self.__setUpListBoxes()
        self.__setUpControlTapeDisplay()
                
    def __setUpFigure(self):
        self.figure=Figure(figsize=(5,5))
        self.worldPlotter=worldPlotter.WorldPlotter3d(self.figure,self.worldObjects.simulationWorld)
        self.figCanvas = FigureCanvasTkAgg(self.figure,master=self.frame)
        self.figCanvas.get_tk_widget().grid(row=1,column=0,columnspan=2)
        

    def __setUpButtons(self):
        self.buttonFrame=ttk.Frame(self.frame)
        self.buttonFrame.grid(row=0,column=0,columnspan=3,sticky="NW")
        self.uploadButton=tkinter.Button(self.buttonFrame,text="Upload build world",command=self.__uploadBuildWorld)
        self.uploadButton.grid(row=0,column=0,sticky="w")
        self.epochButton = tkinter.Button(self.buttonFrame,text="Next Generation",command=self.__nextEpoch)
        self.epochButton.grid(row=0,column=1,sticky="w")
        self.decaEpochButton = tkinter.Button(self.buttonFrame,text="Next 10 Generation",command=self.__next10Epoch)
        self.decaEpochButton.grid(row=0,column=2,sticky="w")
        self.centuryEpochButton = tkinter.Button(self.buttonFrame,text="Next 100 Generation",command=self.__next100Epoch)
        self.centuryEpochButton.grid(row=0,column=3,sticky="w")   
        self.simulateButton=tkinter.Button(self.buttonFrame,text="Simulate control tape",command=self.__simulateTape)
        self.simulateButton.grid(row=0,column=4,sticky="w")
        
    
    def __setUpListBoxes(self):
        intialGenName="Gen "+str(self.nextGenerationIndex)
        self.generationNames.append(intialGenName)
        self.generationsListBox=self._makeListBox(self.frame,[intialGenName],height=20,scrollBar=True)
        self.speciesListBox=self._makeListBox(self.frame,[],height=20,scrollBar=True)
        self.generationsListBox.grid(row=1,column=3,rowspan=1)
        self.speciesListBox.grid(row=1,column=4,rowspan=1)
        #set on click listner
        self.generationsListBox.bind('<<ListboxSelect>>', self.__onGenerationSelect)
        self.speciesListBox.bind('<<ListboxSelect>>',self.__onSpecieSelect)

    def __setUpControlTapeDisplay(self):
        #setting up tape frame
        self.tapeFrame=ttk.Frame(self.frame)
        self.tapeFrame.grid(row=1,column=5,sticky="NW")
        self.fitnessLabel=tkinter.Label(self.tapeFrame,text="FITNESS")
        self.fitnessLabel.grid(row=0,sticky="NW")
        #setting up photo image and label
        self.images=[]
        self.controlTapePhotoImagesList=[]
        self.tapeDisplaysTextList=[]
        self.tapeDisplaysList=[]
        width=self.TAPE_IMAGE_SIZE[0]
        height=self.TAPE_IMAGE_SIZE[1]
        emptyPILImage = Image.new('RGB', (width, height))
        self.emptyPILImage=emptyPILImage
        for i in range(15):
            #tapeName = tkinter.Label(self.tapeFrame,text="")
            #tapeName.grid(row=i,column=0)
            photoImage = ImageTk.PhotoImage(emptyPILImage)
            tapeDisplay = tkinter.Label(self.tapeFrame,image=photoImage)
            #prevents labels from being garbage collected
            self.tapeDisplaysList.append(tapeDisplay)
            self.images.append(emptyPILImage)
            self.controlTapePhotoImagesList.append(photoImage)
            #self.tapeDisplaysTextList.append(tapeName)
            tapeDisplay.grid(row=i+1,column=0)

    def __setUpSimulationChamber(self):
        self.simulationChamber=emSimulation.EMControlledChamber(self.simulationWorld)
    
    def __uploadBuildWorld(self):
        print("upload build world")
        copiedList=copy.deepcopy(self.worldObjects.buildWorld)
        #update with new ids
        worldObjects={}
        for i in copiedList:
            copiedObject=copiedList[i]
            worldObjects[id(copiedObject)]=copiedObject
        self.simulationWorld=worldObjects
        self.simulationWorld[id(self.testCharge)]=self.testCharge
        self.simulationChamber.resetWorldObject(self.simulationWorld)
        self.evolutionChamber.resetWorldObject(self.simulationWorld)
        self.simulationChamber.reset()
        self.worldPlotter.resetWrold(self.simulationWorld)
        self.update()
        
    def __nextEpoch(self):
        genName="Gen "+str(self.nextGenerationIndex)
        self.generationNames.append(genName)
        self.generationsListBox.insert(tkinter.END, genName)
        self.evolutionChamber.epoch()        
    
    def __next10Epoch(self):
        for i in range(10):
            self.__nextEpoch()
            print("GENERATION" + str(i))
    def __next100Epoch(self):
        for i in range(3000):
            self.__nextEpoch()
            print("GENERATION" + str(i))
    
    
    
    def __updateTestCharge(self,position):
            self.testCharge.position=position
            self.update()
            
    def __simulateTape(self):
        #find which specie is selected
        selectedGenName=self.generationsListBox.get(tkinter.ACTIVE)
        generationIndex=self.generationNames.index(selectedGenName)
        selectedSpecieName=self.speciesListBox.get(tkinter.ACTIVE)
        selectedSpecieIndex=self.specieNameList.index(selectedSpecieName)
        controlTape=self.evolutionChamber.populationOverGenerations[generationIndex][selectedSpecieIndex]
        #set the tape on the simulation Chamber
        self.simulationChamber.controlTape=controlTape
        maxTime=9
        self.simulationChamber.runSimulation(maxTime)
        positionOverTime=self.simulationChamber.positionOverTime
        for i in range(len(positionOverTime)):
            position=positionOverTime[i]
            self.frame.after(1*i, self.__updateTestCharge,(position))
        self.simulationChamber.reset()

                
        
    def __updateSpecieListBox(self,generationIndex):
        #delete all elements (from 0 to end)
        self.speciesListBox.delete(0, tkinter.END)
        population=self.evolutionChamber.populationOverGenerations[generationIndex]
        self.specieNameList=[]
        for specieIndex in range(len(population)):
            specieName="Specie "+str(specieIndex)
            self.speciesListBox.insert(tkinter.END,specieName)
            self.specieNameList.append(specieName)
        
            
    def __onGenerationSelect(self,*args):
        selectedGenName=self.generationsListBox.get(tkinter.ACTIVE)
        generationIndex=self.generationNames.index(selectedGenName)
        self.__updateSpecieListBox(generationIndex)




    def __updateControlTapeDisplay(self,generationIndex,specieIndex):
        population=self.evolutionChamber.populationOverGenerations[generationIndex]
        #create new tapeImage
        newSpecie=population[specieIndex].copy()
        tapeImage=tape2PIL.tape2PILImage(newSpecie,self.MIN_PD,self.MAX_PD)
        tapeImagePhotoImage=ImageTk.PhotoImage(tapeImage)
        self.controlTapePhotoImagesList.append(tapeImagePhotoImage)
        for i in range(len(self.tapeDisplaysList)):
            tapeDisplay=self.tapeDisplaysList[i]
            emptyImage=ImageTk.PhotoImage(self.emptyPILImage)
            tapeDisplay.configure(image=emptyImage)
            photoImageToShow=""
            photoImageToShow=self.controlTapePhotoImagesList[-(1+i)]
            tapeDisplay.configure(image=photoImageToShow)
        
    def __updateSPecieFitness(self,generationIndex,specieIndex):
        fitnessOverGenerations=self.evolutionChamber.populationFitnessOverGenerations
        if(len(fitnessOverGenerations)<=generationIndex):
            self.fitnessLabel.config(text="Fitness not evaluated yet")
        else:
            specieFitness=fitnessOverGenerations[generationIndex][specieIndex]
            self.fitnessLabel.config(text="Fitness is: "+str(specieFitness))


    def __onSpecieSelect(self,*args):
        selectedGenName=self.generationsListBox.get(tkinter.ACTIVE)
        generationIndex=self.generationNames.index(selectedGenName)
        selectedSpecieName=self.speciesListBox.get(tkinter.ACTIVE)
        selectedSpecieIndex=self.specieNameList.index(selectedSpecieName)
        self.__updateControlTapeDisplay(generationIndex,selectedSpecieIndex)
        self.__updateSPecieFitness(generationIndex,selectedSpecieIndex)

    #itterates automatically
    @property
    def nextGenerationIndex(self):
        indexToReturn=self._nextGenIndex
        self._nextGenIndex+=1
        return indexToReturn
    #is called in every game loop
    def update(self):
        self.worldPlotter.showWorld()
        self.figCanvas.draw()
            
        
        
#deals with everything to do with build tab require window class as param
class BuilderTab(Tab):
    def __init__(self,mainWindow,frameName):
        super().__init__(mainWindow,frameName)
        #constructing world objects
        self.buildWorld=self.worldObjects.buildWorld

        #click related
        self.selectedObjId=None
        self.selectedView=None
        self.lastMousePosition=(0,0)
        self.dragging=False
        
        #for plotting
        self.plotFigures={"3d":None,"top":None,"front":None,"right":None}
        self.worldPlotters={"3d":None,"top":None,"front":None,"right":None}
        self.figCanvas={"3d":None,"top":None,"front":None,"right":None}
        self.viewPlane={"top":("x","y"),"front":("x","z"),"right":("y","z")}

        self.__setUpWidgets()
        self.update()
        
    def __setUpWidgets(self):
        self.__setUpFigure()
        self.__setUpPlotters()
        self.__setUpObsticlePalette()
        self.__setUpFieldViewPalette()
        
    def __setUpFigure(self,size=(3,3)):
        canvasPosition={"3d":[0,0],"top":[0,1],"front":[1,0],"right":[1,1]}
        for view in ["3d","top","front","right"]:
            figure=Figure(figsize=size)
            #fig canvas is used to convert plt fig to griddable widget
            figCanvas = FigureCanvasTkAgg(figure,master=self.frame)
            figWidget=figCanvas.get_tk_widget()
            #grid it
            row=canvasPosition[view][0]
            column=canvasPosition[view][1]
            figWidget.grid(row=row,column=column)
            #set click listenrs
            self.__setMouseEventListners(figure)
            #asign them to attributs
            self.plotFigures[view]=figure
            self.figCanvas[view]=figCanvas
    
    def __setUpPlotters(self):
        for view in ["3d","top","front","right"]:
            figure=self.plotFigures[view]
            world=self.buildWorld
            if(view =="3d"):
                plotter=self._setUpWorldPlotter3d(figure,world)
            elif(view in ["top","front","right"]):
                plane=self.viewPlane[view]
                plotter=self._setUpWroldPlotter2d(figure,world,plane)
            self.worldPlotters[view]=plotter
    
    def __setMouseEventListners(self,figure):
        #called when artist is clicked
        listnerMethod=self.__onArtClick
        figure.canvas.mpl_connect('pick_event', listnerMethod)
        #called when click button is released
        listnerMethod=self.__onClickRelease
        figure.canvas.mpl_connect('button_release_event', listnerMethod)
        #called when mouse is moved
        listnerMethod=self.__onMouseMove
        figure.canvas.mpl_connect('motion_notify_event', listnerMethod)
    
    #must be called after the figs are set up
    def __setUpObsticlePalette(self):
        #setting up menu frame
        menuFrame=ttk.Frame(self.frame)
        menuFrame.grid(row=0,column=3,sticky="N")
        
        #setting up buttons
            #setting up frame for buttons
        addRemoveButtonFrame=ttk.Frame(menuFrame)
        addRemoveButtonFrame.grid(row=0,column=0,columnspan=2)
        addButton = tkinter.Button(addRemoveButtonFrame, text="Add", command=self.__addObsticle)
        addButton.grid(row=0,column=0, columnspan=1)
        removeButton = tkinter.Button(addRemoveButtonFrame, text="Remove")
        removeButton.grid(row=0,column=1, columnspan=1)
        
        #setting up list menu
        buildableObjectNames=self.mainWindow.constants.buildableObjectNames
        self.obsticlesListBox=self._makeListBox(menuFrame,buildableObjectNames)
        self.obsticlesListBox.grid(column=0,row=1)


    def __setUpFieldViewPalette(self):
        #setting up frame for the radio buttons
        paletteFrame=ttk.Frame(self.frame)
        paletteFrame.grid(row=0,column=4,sticky="NE")
        
        title=tkinter.Label(paletteFrame,text="Field View Options")
        title.grid(row=1)
        
        #the toggle button will asign the value to fieldRadioStatus variable
        self.fieldRadioStatus=tkinter.IntVar()
        onClick=self.__fieldOptionChanged
        noFieldButton=tkinter.Radiobutton(paletteFrame, text="No field",variable=self.fieldRadioStatus, value=0,command=onClick)
        eFieldButton=tkinter.Radiobutton(paletteFrame, text="E field",variable=self.fieldRadioStatus, value=1,command=onClick)
        bFieldButton=tkinter.Radiobutton(paletteFrame, text="B field",variable=self.fieldRadioStatus, value=2,command=onClick)
        
        noFieldButton.grid(row=2)
        eFieldButton.grid(row=3)
        bFieldButton.grid(row=4)
    
    def __fieldOptionChanged(self):
        fieldType=""
        print("radio status")
        if(self.fieldRadioStatus.get()==0):
            fieldType=None
        elif(self.fieldRadioStatus.get()==1):
            fieldType="E"
        elif(self.fieldRadioStatus.get()==2):
            fieldType="B"
        #change vector field type in 3d world plotter
        self.worldPlotters["3d"].changeVectorFieldType(fieldType)
        self.update()
        
    ###Button Listners#########################################################
    #called by addButton
    def __addObsticle(self):
        #find what obsticle to add
        selectedObsticle=self.obsticlesListBox.get(tkinter.ACTIVE)
        initialPosition=np.zeros((3,1),dtype=np.float)
        #if pointCharge 
        obsticle=None
        if(selectedObsticle=="Point Charge"):
            obsticle=emObjects.PointCharge(initialPosition)
            print("obsticle: ", id(obsticle))
            """self.buildWorldObject[id(obsticle)]=obsticle"""
        #adding magnetic field
        elif(selectedObsticle == "Uniform Magnetic Field"):
            obsticle=emObjects.UniformMagneticField(initialPosition)
 
            print("magnetic field made")
        #adding charge plates
        elif(selectedObsticle == "Plate Charge"):
            obsticle=emObjects.PlateCharge(initialPosition)
        elif(selectedObsticle=="Positive Enforcement Token"):
            obsticle=emObjects.PositiveEnforcementToken(initialPosition)
        elif(selectedObsticle=="Negative Enforcement Token"):
            obsticle=emObjects.NegativeEnforcementToken(initialPosition)
        if(obsticle!=None):
            #add the object instant to build world object list
            self.buildWorld[id(obsticle)]=obsticle
        else:
            print(selectedObsticle)
        
        self.update()

    def __removeObsticle(self):
        pass
    
    ##Click Listners###########################################################
    
    def __findSelectedViewFromArt(self,art):
        selectedView=False
        for view in self.worldPlotters:
            #if clicked artist is in the artIdObjId of the view, then artist was selected in this view
            plotter=self.worldPlotters[view]
            artIdInPlotter=plotter.artIdList
            if(id(art) in artIdInPlotter):
                selectedView=view
        return selectedView 
    
    def __findObjIdFromArt(self,art,selectedView):
        #if clicked artist is in the artIdObjId of the view, then artist was selected in this view
        plotter=self.worldPlotters[selectedView]
        selectedObjId=plotter.artId2ObjIdDict[id(art)]
        return selectedObjId
                    
    def __onArtClick(self,event):
        print("art clicked")
        art=event.artist
        selectedView=self.__findSelectedViewFromArt(art)
        if(selectedView!=False):
            objId=self.__findObjIdFromArt(art,selectedView)
            self.selectedView=selectedView
            self.selectedObjId=objId
            print("art found")                
        
    #called when click button is released
    def __onClickRelease(self,event):
        #resetting dragging parameters
        self.dragging=False
        self.selectedObjId=None
        print("released")
        
    
    def __findMouseDistanceMoved(self,cursorX,cursorY):
        #find cursor distance moved
        dxMouse=cursorX-self.lastMousePosition[0]
        dyMouse=cursorY-self.lastMousePosition[1]
        self.lastMousePosition=[cursorX,cursorY]
        return dxMouse,dyMouse
    
    def __findTranslationVector(self,cursorX,cursorY):
        dxMouse,dyMouse = self.__findMouseDistanceMoved(cursorX,cursorY)
        #dimention used in plane e.g. (z,y)=>varToSwapXBy=z,varToSwapyBy=y
        axisRepresentedByX=self.viewPlane[self.selectedView][0]
        axisRepresentedByY=self.viewPlane[self.selectedView][1]
        #xyz represented in 0,1,2 e.g. y=>1
        axisRepresentedByXIndex=["x","y","z"].index(axisRepresentedByX)
        axisRepresentedByYIndex=["x","y","z"].index(axisRepresentedByY)
        #make translation vector
        translationVector=np.zeros((3,1),dtype=np.float)
        translationVector[axisRepresentedByXIndex,0]=dxMouse
        translationVector[axisRepresentedByYIndex,0]=dyMouse
        return translationVector
        
        
        
    #called when mouse is moved
    def __onMouseMove(self,event):
        if(event.button==1):
            #left button is clicked
            if(event.xdata!=None and event.ydata!=None and self.selectedObjId!=None):
                #inside text box and an element is selected
                if(self.dragging==False):
                    self.dragging=True
                    #record the position where mouse started dragging
                    self.lastMousePosition=(event.xdata,event.ydata)
                else:
                    objToMove=self.buildWorld[self.selectedObjId]
                    cursorX=event.xdata
                    cursorY=event.ydata
                    #find vector to translate object by
                    translationVector=self.__findTranslationVector(cursorX,cursorY)
                    #translate the object
                    objToMove.translatePosition(translationVector)
                    #update figures                    
                    self.update()
 
        elif None:
            #mouse is not clicked
            self.__onFigRelease()
            print(event.button)

        
    def update(self):
        for viewName in self.worldPlotters:
            self.worldPlotters[viewName].showWorld()

        for viewName in self.figCanvas:
            self.figCanvas[viewName].draw()
