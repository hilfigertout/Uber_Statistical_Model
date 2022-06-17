import random as r
import math
#import matplotlib.pyplot as plotter
import numpy
import scipy
from scipy import stats

# Rideshare service model with the probability an assault occurs on a given ride decreased from the baseline.
# Original: 0.5, New: 0.4 
# Author: Ian Roberts

# See Uber_Model_baseline file for sources and derivations



class Board:
    #ADJUSTABLE VARIABLES
    numDrivers = 1000       #NUMBER OF DRIVERS IN THE SIMULATION
    numDays = 50            #NUMBER OF DAYS THE SIMULATION RUNS FOR
    probMalicious = 0.005   #PROBABILITY A DRIVER OR RIDER IS MALICIOUS
    probAssault = 0.4	 #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
    ridersPer = 22.2             #NUMBER OF RIDERS GENERATED PER DRIVER
    mTw = 0.95                 #PROBABILITY A MALICIOUS MAN TARGETS WOMEN
    wTm = 0.95                 #PROBABILITY A MALICIOUS WOMAN TARGETS MEN
    pMM = 0.7639        #PROBABILITY A MALICIOUS PERSON IS A MAN  
    expectedRides = 3.444*numDays*numDrivers    #AVERAGE NUMBER OF RIDES EXPECTED OVER THE COURSE OF THE SIMULATION
    expectedAssaults = 0.4033*numDrivers        #AVERAGE NUMBER OF ASSAULTS EXPECTED OVER THE COURSE OF THE SIMULATION

    def __init__(self):
        self.mTm = 1 - self.mTw              #PROBABILITY A MALICIOUS MAN TARGETS OTHER MEN
        self.wTw = 1 - self.wTm              #PROBABILITY A MALICIOUS WOMAN TARGETS OTHER WOMEN
        self.probMaliciousGivenMan = self.probMalicious*self.pMM*2         #PROBABILITY A MAN IS MALICIOUS
        self.probMaliciousGivenWoman = self.probMalicious*(1-self.pMM)*2   #PROBABILITY A WOMAN IS MALICIOUS
        self.setDrivers = set()       #SET OF DRIVERS IN THE SIMULATION
        self.setRiders = set()       #SET OF RIDERS IN THE SIMULATION
        self.day = 0                #GETTER FOR CURRENT DAY
        self.assaults = []          #TRACKS ASSAULTS BY DAY 
        self.rides = []             #TRACKS TOTAL RIDES BY DAY
        self.activeRiders = set()      #SET OF RIDERS WHO NEED A RIDE THAT DAY
        self.activeDrivers = set()     #SET OF DRIVERS WHO CAN STILL GIVE A RIDE THAT DAY
        self.driversToRemove = set()   #SET OF DRIVERS NOT ACTIVE AFTER EACH BATCH OF RIDES
        
        for i in range(self.numDrivers):                             #Generate Driveres      
            self.setDrivers.add(Driver(self))

        for i in range(int(self.ridersPer*self.numDrivers)):         #Generate riders
            self.setRiders.add(Rider(self))
        
        for driver in (self.setDrivers):
            driver.findRidersInRange(self)

        for rider in self.setRiders:
            active = rider.nextDay()
            if (active):
                self.activeRiders.add(rider)
        for driver in self.setDrivers:
            driver.nextDay()
        # print("simulation setup complete")


    #Runs the simulation
    def runSim(self):
        for day in range(self.numDays):
            self.assaults.append(0)
            self.rides.append(0)
            self.day = day
            self.activeDrivers = self.setDrivers.copy()

            while (len(self.activeDrivers) > 0 and len(self.activeRiders) > 0):
                for driver in self.activeDrivers:         
                    riderToRemove = driver.giveRide(self)
                    if (riderToRemove is None):
                        self.driversToRemove.add(driver)
                    else:
                        self.activeRiders.remove(riderToRemove)
                for driver in self.driversToRemove:
                    self.activeDrivers.remove(driver)
                self.driversToRemove.clear()
            self.activeRiders.clear()                      #Reset for next day
            self.activeDrivers.clear()
            for rider in self.setRiders:
                active = rider.nextDay()
                if (active):
                    self.activeRiders.add(rider)
            for driver in self.setDrivers:
                driver.nextDay()

            #print("Day " + str(day + 1) + " completed")


class Driver:
    #ADJUSTABLE VARIABLES
    probMale = 0.639             #PROBABILITY THE DRIVER IS MALE
    radius = 1                  #RADIUS THE DRIVER CAN GIVE RIDES IN

    def __init__(self, board):
        self.ridesGiven = 0            #NUMBER OF RIDES GIVEN THAT DAY
        self.male = False               #INDICATES THE SEX OF THE DRIVER
        self.targetWomen = None         #IF MALICIOUS, INDICATES TARGET SEX
        self.coords = (r.uniform(0, 10), r.uniform(0, 10))  #COORDINATES OF THE DRIVER
        self.ridersInRange = set()      #SET OF THE RIDERS IN RANGE OF THE DRIVER
        self.activeInRange = []         #LIST OF ACTIVE RIDERS IN RANGE  
        self.isMalicious = False       #MALICIOUS INDICATOR

        if (r.random() < self.probMale):
            self.male = True
            if (r.random() < board.probMaliciousGivenMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        else:
            self.male = False
            if (r.random() < board.probMaliciousGivenWoman):
                self.isMalicious = True
                if (r.random() < board.wTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False

    #Populates the driver's ridersInRange set. 
    #Must be called AFTER all of the riders have been generated.
    def findRidersInRange (self, board):
        for rider in board.setRiders:
            x = rider.coords[0] - self.coords[0]
            y = rider.coords[1] - self.coords[1]
            if (x*x + y*y <= self.radius*self.radius):
                self.ridersInRange.add(rider)

    #Finds the riders in range that need a ride that day.
    #Requires that self.ridersInRange has been populated.
    def findActiveInRange(self):
        for rider in self.ridersInRange:
            if (rider.needRide):
                self.activeInRange.append(rider)
        r.shuffle(self.activeInRange)

    #Resets the driver for the next day.
    #Must be called AFTER the all of the riders are prepared
    #for the next day. 
    def nextDay(self):
        self.ridesGiven = 0
        self.activeInRange.clear()
        self.findActiveInRange()
        
        
    #Returns alias to rider if driver gave a ride to that rider.
    #Returns None if the driver cannot give any more rides that day.
    def giveRide(self, board):
        rider = None
        if (len(self.activeInRange) > 0 and self.ridesGiven < 10):
            rider = self.activeInRange.pop(0)
            while (not (rider in board.activeRiders) and (not (rider is None))):
                if (len(self.activeInRange) > 0):
                    rider = self.activeInRange.pop(0)
                else:
                    rider = None
            if (not rider is None):
                assaultHappened = False
                board.rides[board.day] = board.rides[board.day] + 1
                if (rider.isMalicious):
                    if ((self.male and not rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs     
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        assaultHappened = True
                    elif ((not self.male and rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        assaultHappened = True
                if (self.isMalicious and not assaultHappened):
                    if ((rider.male and not self.targetWomen) and (r.random() < board.probAssault)):   #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                    elif ((not rider.male and self.targetWomen) and (r.random() < board.probAssault)): #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
        return rider


            

class Rider:
    # ADJUSTABLE VARIABLES
    probNeedRide = 0.1552             #PROBABILITY RIDER NEEDS A RIDE
    probMale = 0.5                      #PROBABILITY THE RIDER IS MALE

    def __init__(self, board):
        self.male = False                   #INDICATES THE SEX OF THE RIDER
        self.needRide = False               #INDICATES IF RIDER NEEDS A RIDE THAT DAY
        self.coords = (r.uniform(0, 10), r.uniform(0, 10))              #COORDINATES OF THE RIDER
        self.targetWomen = None             #IF MALICIOUS, INDICATES PREFERRED TARGET SEX
        self.isMalicious = False            #MALICIOUSNESS INDICATOR
        if (r.random() < self.probMale):
            self.male = True
            if (r.random() < board.probMaliciousGivenMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        else:
            self.male = False
            if (r.random() < board.probMaliciousGivenWoman):
                self.isMalicious = True
                if (r.random() < board.wTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False

    #Resets the rider for the next day.
    def nextDay(self):
        self.needRide = False
        if (r.random() < self.probNeedRide):
            self.needRide = True
        return self.needRide





        


#MAIN CODE

r.seed(1234)		#Set Seed
total_assaults = []	#List to store the total number of assaults per simulation
total_rides = []    #List to store the total number of rides per simulation
for i in range(50):	#Run 50 simulations
    b = Board()
    b.runSim()
    print("Simulation " + str(i + 1) + " complete! ")
    total_assaults.append(sum(b.assaults))
    total_rides.append(sum(b.rides))


#Print Data:
print("Total rides in each sim: ")
print(str(total_rides))
print("Total assaults in each sim: ")
print(str(total_assaults))
print()

# Significance tests
print("Rides test: ")
alpha = 0.05
print("Ho: mu = " + str(Board.expectedRides))
print("Ha: mu != " + str(Board.expectedRides))
print("Significance level = " + str(alpha))
print("average rides per sim: " + str(numpy.mean(total_rides)))
s, p = scipy.stats.ttest_1samp(total_rides, Board.expectedRides, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))
print()

print("Assaults test: ")
alpha = 0.05
print("Ho: mu = " + str(Board.expectedAssaults))
print("Ha: mu != " + str(Board.expectedAssaults))
print("Significance level = " + str(alpha))
print("mean assaults: " + str(numpy.mean(total_assaults)))
s, p = scipy.stats.ttest_1samp(total_assaults, Board.expectedAssaults, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))




