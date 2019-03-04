import guiClean as gui
import worldConstants
import worldObjects as wo

def main():
    constants=worldConstants.WorldConstants()
    worldObjects=wo.WorldObjects()
    myWindow = gui.MainWindow(constants,worldObjects)
    myWindow.update()
    
    while True:
        myWindow.update()
    
if(__name__=="__main__"):
    main()