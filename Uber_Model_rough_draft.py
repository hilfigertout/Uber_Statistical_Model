import random as r
import math
import numpy
import scipy
from scipy import stats

# Rough Draft for rideshare service model
# Author: Ian Roberts

# Sources and Derivations: 

# In 2019 and 2020, there were 5 million Uber drivers. For those 5 million drivers, Uber claims to have 111 million average monthly users.
    # This means an average of 22.2 riders per driver. We will generate 22.2*d riders and scatter them
    # randomly about the board. 

#For those 5 million drivers, Uber claims there were 17.22 million trips per day, on average. 
    # This means that each driver makes an average of 3.444 trips per day. So for a 22.2 riders per driver,
    # we can say the probability a rider needs a ride is 0.1551
    # For 1000 drivers, we expect to see approx. 3444 rides per day, 172200 rides over 50 days.
    # Running the sim while counting the number of rides with this parameter shows that it works. 

# In 2018, Uber reported 3045 sexual assaults in 1.3 billion rides 
    # Assuming this rate of "assaults per ride" still holds, we expect to see about 0.438 assaults in the fifty days of 
    # our simulation. Since that's absoultely tiny, we are going to artificially scale it up by a factor of 1000 so the variations
    # are visible. Thus, we expect to see about 403.3 assaults per 50-day sim, on average. 

# The probability of an assault happening on a ride is assumed to be equal to the probability that at least one of the
# riders is malicious AND that an assault happens. 
    # We will fix the probability that an assault happens on a ride with a malicious
    # person at 50%. The parameter to be adjusted in order to tune the model to match reality is the proportion of malicious people
    # in the model. (While this joint probability is going to be 1000 times as high as real life, we cannot say for certain if our 
    # model has 1000 times as many malicious people as real life.)


class Board:
    #ADJUSTABLE VARIABLES
    numDrivers = 1000       #NUMBER OF DRIVERS IN OUR MODEL
    numDays = 50            #NUMBER OF DAYS THE MODEL RUNS FOR
    probMalicious = 0.002276   #PROBABILITY A DRIVER OR RIDER IS MALICIOUS
    assaultsPerRide = 0.002357      #AVERAGE NUMBER OF ASSAULTS PER RIDE, APPROX. 1000 TIMES REAL LIFE.
    ridersPer = 22.2              #NUMBER OF RIDERS GENERATED PER DRIVER
    expectedRides = 3.444*numDays*numDrivers    #AVERAGE NUMBER OF RIDES EXPECTED FROM THE SIMULATION
    expectedAssaults = 0.4033*numDrivers        #AVERAGE NUMBER OF ASSAULTS EXPECTED FROM THE SIMULATION

    def __init__(self):

        self.probAssault = 0.5      #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
        self.setDrivers = set()       #SET OF DRIVERS IN THE SIMULATION
        self.setRiders = set()       #SET OF RIDERS IN THE SIMULATION
        self.day = 0                #GETTER FOR CURRENT DAY
        self.assaults = []          #TRACKS ASSAULTS BY DAY 
        self.rides = []             #TRACKS RIDES BY DAY
        self.activeRiders = set()      #SET OF RIDERS WHO NEED A RIDE THAT DAY
        self.activeDrivers = set()     #SET OF DRIVERS WHO CAN STILL GIVE A RIDE THAT DAY
        self.driversToRemove = set()   #SET OF DRIVERS NOT ACTIVE AFTER EACH BATCH OF RIDES
        
        for i in range(self.numDrivers):
            self.setDrivers.add(Driver(self))

        for i in range(int(self.ridersPer*self.numDrivers)):         #Generate 20 riders per driver
            self.setRiders.add(Rider(self))

        for driver in (self.setDrivers):
            driver.findRidersInRange(self)

        for rider in self.setRiders:
            active = rider.nextDay()
            if (active):
                self.activeRiders.add(rider)
        for driver in self.setDrivers:
            driver.nextDay()
        #print("simulation setup complete")



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

            #print("Day " + str(day) + " completed")


class Driver:
    radius = 1                 #RADIUS THE DRIVER CAN GIVE RIDES IN
    def __init__(self, board):
        self.ridesGiven = 0            #NUMBER OF RIDES GIVEN THAT DAY
        self.coords = (r.uniform(0, 10), r.uniform(0, 10))  #COORDINATES OF THE DRIVER
        self.ridersInRange = set()      #SET OF THE RIDERS IN RANGE OF THE DRIVER
        self.activeInRange = []         #LIST OF ACTIVE RIDERS IN RANGE  
        self.isMalicious = False       #MALICIOUS INDICATOR
        if (r.random() < board.probMalicious):
            self.isMalicious = True

    #Enumerates the riders within range of the driver. 
    def findRidersInRange (self, board):
        for rider in board.setRiders:
            x = rider.coords[0] - self.coords[0]
            y = rider.coords[1] - self.coords[1]
            if (x*x + y*y <= self.radius*self.radius):
                self.ridersInRange.add(rider)

    #Determines which of the riders in range of the driver are active
    def findActiveInRange(self):
        for rider in self.ridersInRange:
            if (rider.needRide):
                self.activeInRange.append(rider)

    #Resets for the next day
    def nextDay(self):
        self.ridesGiven = 0
        self.activeInRange.clear()
        self.findActiveInRange()
        
        
    #Returns alias to rider if driver gave a ride to that rider.
    #Returns none if the driver cannot give any more rides that day.
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
                board.rides[board.day] = board.rides[board.day] + 1
                if ((self.isMalicious or rider.isMalicious) and (r.random() < board.probAssault)):  #Assault occurs     
                    board.assaults[board.day] = board.assaults[board.day] + 1
                    self.ridersInRange.remove(rider)
        return rider


class Rider:
    probNeedRide = 0.1552                #PROBABILITY RIDER NEEDS A RIDE
    def __init__(self, board):
        self.needRide = False               #INDICATES IF RIDER NEEDS A RIDE THAT DAY
        self.coords = (r.uniform(0, 10), r.uniform(0, 10))              #COORDINATES OF THE RIDER
        self.isMalicious = False            #MALICIOUSNESS INDICATOR
        if (r.random() < board.probMalicious):
            self.isMalicious = True

    #Resets for the next day
    def nextDay(self):
        self.needRide = False
        if (r.random() < self.probNeedRide):
            self.needRide = True
        return self.needRide






r.seed(1851)		#Set Seed
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


print("Assaults test: ")
alpha = 0.05
print("Ho: mu = " + str(Board.expectedAssaults))
print("Ha: mu != " + str(Board.expectedAssaults))
print("Significance level = " + str(alpha))
print("mean assaults: " + str(numpy.mean(total_assaults)))
s, p = scipy.stats.ttest_1samp(total_assaults, Board.expectedAssaults, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))
