import random as r
import math

# Rough Draft for Uber Model
# Author: Ian Roberts



class Board:
    numDrivers = 1000       #NUMBER OF DRIVERS IN OUR MODEL
    numDays = 50            #NUMBER OF DAYS THE MODEL RUNS FOR
    probMalicious = 0.02819   #PROBABILITY A DRIVER OR RIDER IS MALICIOUS
    
    def __init__(self):
        self.ridersPer = 20.6              #NUMBER OF RIDERS GENERATED PER DRIVER
        self.probAssault = 0.02678 / self.probMalicious       #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
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
            rx = r.uniform(0, 10)
            ry = r.uniform(0, 10)
            self.setRiders.add(Rider(self, rx, ry))

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
        xcoord = r.uniform(0, 10)
        ycoord = r.uniform(0, 10)
        self.coords = (xcoord, ycoord)  #COORDINATES OF THE DRIVER
        self.ridersInRange = set()      #SET OF THE RIDERS IN RANGE OF THE DRIVER
        self.activeInRange = []         #LIST OF ACTIVE RIDERS IN RANGE  
        self.isMalicious = False       #MALICIOUS INDICATOR
        if (r.random() < board.probMalicious):
            self.isMalicious = True

    def findRidersInRange (self, board):
        for rider in board.setRiders:
            x = rider.coords[0] - self.coords[0]
            y = rider.coords[1] - self.coords[1]
            if (x*x + y*y <= self.radius*self.radius):
                self.ridersInRange.add(rider)

    def findActiveInRange(self):
        for rider in self.ridersInRange:
            if (rider.needRide):
                self.activeInRange.append(rider)

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
    probNeedRide = 0.181                #PROBABILITY RIDER NEEDS A RIDE
    def __init__(self, board, rx, ry):
        self.needRide = False               #INDICATES IF RIDER NEEDS A RIDE THAT DAY
        self.coords = (rx, ry)              #COORDINATES OF THE RIDER
        self.isMalicious = False            #MALICIOUSNESS INDICATOR
        if (r.random() < board.probMalicious):
            self.isMalicious = True

    def nextDay(self):
        self.needRide = False
        if (r.random() < self.probNeedRide):
            self.needRide = True
        return self.needRide







r.seed(1225)
totalAssaults = []
totalRides = []
for i in range(50):
    b = Board()
    b.runSim()
    totalAssaults.append(sum(b.assaults))
    totalRides.append(sum(b.rides))
    print("sim " + str(i) + " completed.")

print("Rides: " + str(totalRides))
meanRides = sum(totalRides)/len(totalRides)
print(str(meanRides))
print("Assaults: " + str(totalAssaults))
meanAssaults = sum(totalAssaults)/len(totalAssaults)
print(str(meanAssaults))
