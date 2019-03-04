class WorldConstants():
      def __init__(self):
          self.buildableObjectNames=["Point Charge","Wire",
                                     "Uniform Magnetic Field","Plate Charge",
                                     "Positive Enforcement Token",
                                     "Negative Enforcement Token"]  
          self.obsticleNamesList=["Point Charge","Wire","Uniform Magnetic Field","Plate Charge","Control Plate"]  
          #k
          self.coulombConstant=8.9875517873681764*(10**9) 
          #myu0 in (N/A2 or T⋅m/A or Wb/(A⋅m) or V⋅s/(A⋅m)) not H/m Henry
          self.magneticPermiability=1.2566370614*(10**(-6)) 
          