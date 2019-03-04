import numpy as np

def varIsValidPoint(var):
    errorMsg=""
    #if numpy array
    if(type(var)==np.ndarray):
        if(var.shape==(3,1)):
            #everything is as expected
            point=var
        elif(len(var.shape)==1 and len(var)==3):
            #convert (3,) array to (3,1)
            point=var.reshape((3, 1))
            print("Point should have shape (3,1) not (3,)")
        else:
            errorMsg="Point must be ndarray with shape (3,1) not %s"%str(var.shape)
            point=None
    #if list
    elif(type(var)==list):
        if(len(var)==3):
            print("Point should be a ndarray not a list")
            numberTypes=(int, float, complex,np.float,np.float16,np.float32,np.float64)
            allNumbers=True
            invalidValue=""
            for value in var:
                if(type(value) not in numberTypes):
                    allNumbers=False
                    invalidValue=value
            point=np.array([[var[0]],[var[1]],[var[2]]])
            #this raise warning because they could be using numpy float etc
            if(not allNumbers):
                print("One of the value in point list was not a number but was a %s"%str(type(invalidValue)))
    #not valid type
    else:
        errorMsg="Point must be ndarray with shape (3,1) not %s type"%str(type(var))
        point=None
    #convert np array dtype to float
    if type(point) ==np.ndarray:
        point=point.astype(np.float32)

    return point,errorMsg
#checks if first argument of a function is a valid 3d vector
def firstArgValidPoint(function):
    def wrapper(*args, **kwarfs):
        firstArg=args[0]
        point,errorMsg=varIsValidPoint(firstArg)
        if type(point)!=np.ndarray:
            if point == None:
                raise ValueError("First argument, "+errorMsg)
        else:
            #substitute the second argument with new argument
            newArgs=(point,)+args[1:]
            #call the original function with new arguments
            return function(*newArgs,**kwarfs)       
    return wrapper
#checks if second argument of a function is a valid 3d vector
def secondArgValidPoint(function):   
    def wrapper(*args, **kwarfs):
        secondArg=args[1]
        point,errorMsg=varIsValidPoint(secondArg)

        if type(point)!=np.ndarray:
            if(point==None):
                raise ValueError("Second argument, "+errorMsg)
        else:
            #substitute the second argument with new argument
            newArgs=args[:1]+(point,)+args[2:]
            #call the original function with new arguments
            return function(*newArgs,**kwarfs)       
    return wrapper