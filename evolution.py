import random
import emSimulation
import numpy as np
import pandas as pd

class evolutionChamber:
    def __init__(self,simulationWorld,popNumber=100,dtTape=0.1,maxT=10,pdMin=-1,pdMax=1):
        self.pdMin=pdMin
        self.pdMax=pdMax
        self.maxT=maxT
        self.dtTape=dtTape
        self.emChamber=emSimulation.EMControlledChamber(simulationWorld,dtStep=dtTape*2)
        #contains obsticles etc
        self.objectWorld=simulationWorld
        
        self.populationResults=[]
        self.populationFitness=[]
        
        #if set to 0.5 then 50% of species are killed without reproducing
        self.reproducibility=0.5
        #if set to 0.1 then 10% of genetic material are ssigned random value 
        self.mutationRate=0.1
        
        initialPopulation=self.initializePopulation(popNumber)
        self.populationOverGenerations=[initialPopulation]
        self.populationFitnessOverGenerations=[]

    
    def makeGeneticMaterial(self):
        geneticMaterial=np.empty((3,1),dtype=np.float)
        pdRange=self.pdMax-self.pdMin
        for dimension in range(3):
            probability=float(random.randint(0,100))/100.0
            geneticMaterial[dimension,0]=self.pdMin+(probability*pdRange)
        return geneticMaterial
            
    def initializePopulation(self,popNumber):
        if(self.dtTape<self.maxT):
            numberOfGenMaterial=int(self.maxT/self.dtTape)
        else:
            raise ValueError("dt must be less than maxT")
        population=[]
        for n in range(popNumber):
            #specie is the controltape
            specie=[]
            for genMaterialIndex in range(numberOfGenMaterial):
                geneticMaterial=self.makeGeneticMaterial()
                specie.append(geneticMaterial)
            population.append(specie)
 
        return population
    
    def examinePopulation(self,population):
        populationResults=[]
        for specie in population:
            self.emChamber.controlTape=specie
            self.emChamber.runSimulation(self.maxT-1)
            specieResult=self.emChamber.getResults()
            populationResults.append(specieResult)
            self.emChamber.reset()
        return populationResults
        
    #assign fitness value to populationResults
    def assignFitnessToResults(self,populationResults):
        populationFitness=[]
        for result in populationResults:
            fitness=(1+result["numOfPosTokensCollected"]*100+
            result["numOfNegTokensCollected"]*-100+
            result["goalReached"]*300)
            populationFitness.append(fitness)
        self.populationFitnessOverGenerations.append(populationFitness)
        return populationFitness
    
    def selectingMatingSpecies(self,populationFitness,numberOfMates):
        #l2 normalization of fitness (L2 express anomoly) ( their square adds up to one)
        normFactor=np.linalg.norm(np.array(populationFitness),ord=2,axis=0)
        normPopFitness=[specieFitness/normFactor for specieFitness in populationFitness]
        #distributing lottery tickets (from 1 to 100) to species
        populationLotteryTickets=[]
        nextTicketNumber=1
        #this value need to be large enough to share the number across population
        maxPossibleNumber=1000
        for normSpecieFitness in normPopFitness:
            if (normSpecieFitness<0):
                #since norm value will be squared making positive, they need to beminimized to be 0
                normSpecieFitness=0
            minTicketNumber=int(nextTicketNumber)
            maxTicketNumber=int(nextTicketNumber+(maxPossibleNumber*(normSpecieFitness**2))-1)
            if(maxTicketNumber==(nextTicketNumber-1)):
                #outside the range no chance
                minTicketNumber=maxPossibleNumber+1
                maxTicketNumber=maxPossibleNumber+2
            else:
                nextTicketNumber=maxTicketNumber+1
            ticketNumber=[minTicketNumber,maxTicketNumber]
            populationLotteryTickets.append(ticketNumber)
        print("ticket")
        print(populationLotteryTickets)
        #drawing picks for the mating population
        matingSpeciesIndex=[]
        for n in range(numberOfMates):
            lotteryDrawNumber=random.randint(1,maxPossibleNumber)
            for ticket in populationLotteryTickets:
                if ticket[0]<=lotteryDrawNumber and ticket[1]>=lotteryDrawNumber:
                    selectedSpecieIndex=populationLotteryTickets.index(ticket)
                    matingSpeciesIndex.append(selectedSpecieIndex)
        return matingSpeciesIndex
    
    @staticmethod #returns a pair of couple's index
    def assignPairs(matingSpeciesIndexes):
        matingPairIndexes=[]
        matesIndexOnWaitingList=matingSpeciesIndexes.copy()
        while (len(matesIndexOnWaitingList)>=2):
            specieIndex=matesIndexOnWaitingList[0]
            #pick a random index excluding youe self
            spouseWatingListIndex=random.randint(1,len(matesIndexOnWaitingList)-1)
            spouseIndex=matesIndexOnWaitingList[spouseWatingListIndex]
            couple=(specieIndex,spouseIndex)
            matingPairIndexes.append(couple)
            #remove them from waiting list
            del matesIndexOnWaitingList[spouseWatingListIndex]
            del matesIndexOnWaitingList[0]
        print("couples")
        print(matingPairIndexes)
        return matingPairIndexes
    
    #randomize the order of list
    def randomizeListOrder(self,listToRandomize):
        listToRandomize=listToRandomize.copy()
        randomizedList=[]
        for n in range(len(listToRandomize)):
            randomChoice=random.choice(listToRandomize)
            randomizedList.append(randomChoice)
            randomChoiceIndex=listToRandomize.index(randomChoice)
            del listToRandomize[randomChoiceIndex]
        return randomizedList
    
    #this method does not give a uniform distribution
    def randomlyDecomposeNumber(self,originalPie,shareBetween,allowZero=False):
        decomposedList=[]
        if allowZero==False:
            if(originalPie<shareBetween):
                raise ValueError("length of originalPie needs to be larger than the number to share it with")
            #add 1 at start if zero is not allowed
            decomposedList=[1 for n in range(shareBetween)]
            originalPie-=shareBetween
        else:
            decomposedList=[0 for n in range(shareBetween)]
        numberLeftToClaim=originalPie
        for index in range(shareBetween-1):
            aDecomposition=random.randint(0,numberLeftToClaim)
            decomposedList[index]+=aDecomposition
            numberLeftToClaim-=aDecomposition
        #last pick gets the left over
        decomposedList[-1]+=numberLeftToClaim
        randomizedDecomposedList=self.randomizeListOrder(decomposedList)
        return randomizedDecomposedList
    """
    @staticmethod
    def geneSegmentsMaker(geneLen,ratioToSelect,minSegmentNum,maxSegmentNum):
        #decide number of segments
        numberOfSegments=int(lenToSelect/random.randint(minSegmentNum,maxSegmentNum))
        segmentLens=randomlyDecomposeNumber(geneLen,)
        #make n number of segment lengths
        segmentLens=[]
        geneStripLeftToClaim=lenToSelect
        for n in range(numberOfSegments,0,-1):
            #-n adjust to leave enough geneSegment out for other segments
            aSegmentLen=random.randint(1,geneStripLenToClaim-n)
            segmentLens.append(aSegmentLen)
            geneStripLeftToClaim-=aSegmentLen
            
        #randomize segmentLens (this needs to be randomized )
        #this is because the first len had larger pie to pick from     
        randomizedSegmentLens=[]
        while(len(segmentLens)>0):
            pickedIndex=random.randint(0,len(segmentLens)-1)
            pickedSegmentLen=segmentLens[lensIndex]
            randomizedSegmentLens.append(thisSegmentLen)
            del segmentLens[lensIndex]
        
        if(lenToSelect!=geneLen):
            """

    def crossOverSpecies(self,population,matingPairIndexes):
        newPopulation=[]
        for coupleIndexes in matingPairIndexes:
            spouseAGene=population[coupleIndexes[0]]
            spouseBGene=population[coupleIndexes[1]]
            newGeneLen=min(len(spouseAGene),len(spouseBGene))
            newGene=[0 for i in range(newGeneLen)]
            #A specie must be longer than 8 since it is split into 8 segments at max
            if(len(population)<8):
                raise ValueError("length of sepcies must be greater than 8")
            numberOfSegments=random.randint(2,8)
            #determine length of each segments
            segmentLens=self.randomlyDecomposeNumber(newGeneLen,numberOfSegments,allowZero=False)
            #slot in the genetic materials
            nextLowerLimit=0
            for n in range(numberOfSegments):
                choseLen=random.choice(segmentLens)
                chosenLenIndex=segmentLens.index(choseLen)
                #select which spouse to slot in A or B
                parentGene=random.choice([spouseAGene,spouseBGene])
                #slot in the genetic material
                lowerLimit=nextLowerLimit
                upperLimit=nextLowerLimit+choseLen
                newGene[lowerLimit:upperLimit]=parentGene[lowerLimit:upperLimit]
                nextLowerLimit+=choseLen
                del segmentLens[chosenLenIndex]
            newPopulation.append(newGene)
        return newPopulation

    def mutatePopulation(self,population,mutationRate):
        #totalLenToMutate=int(population*mutationRate)
        populationToMutate=population.copy()
        mutatedPopulation=[]
        for specie in populationToMutate:
            for i in range(len(specie)):
                randomNumber=random.randint(1,100)
                if(randomNumber<mutationRate*100):
                    specie[i]=self.makeGeneticMaterial()
            mutatedPopulation.append(specie)
        return mutatedPopulation
    
    def epoch(self):
        print("epoch started")
        currentPopulation=self.populationOverGenerations[-1]
        print("population length is",len(currentPopulation))
        print("examine population")
        populationResults=self.examinePopulation(currentPopulation)
        print("assignFitness")
        populationFitness=self.assignFitnessToResults(populationResults)
        #numberOfMates=len(currentPopulation)*2        
        numberOfMates=100*2   
        print("selecting mating species")
        matingSpeciesIndex=self.selectingMatingSpecies(populationFitness,numberOfMates)
        print("number of mating species")
        print(len(matingSpeciesIndex))
        print("mating pair index")
        matingPairsIndex=self.assignPairs(matingSpeciesIndex)
        print("Number of mating pairs")
        print(len(matingPairsIndex))
        newPopulation=self.crossOverSpecies(currentPopulation,matingPairsIndex)
        print("newPopLen")
        print(len(newPopulation))
        newMutatedPopulation=self.mutatePopulation(newPopulation,self.mutationRate)
        self.populationOverGenerations.append(newMutatedPopulation)
        print("mutated")
        print(len(newMutatedPopulation))
        
    def resetWorldObject(self,newWorld):
        self.emChamber.resetWorldObject(newWorld)
        self.objectWorld=newWorld

  
        