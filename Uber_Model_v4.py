import random as r
import math
#import matplotlib.pyplot as plotter
import numpy
import scipy
from scipy import stats

# Rideshare service model, tuned to match our expectations of reality
# Author: Ian Roberts

# Sources and Derivations: 

# In 2019 and 2020, there were 5 million Uber drivers and 18.7 million trips per day, on average. (Source 1)
    # This means that each driver makes an average of 3.74 trips per day. So for a minimum of 20 riders per driver,
    # we will say the probability a rider needs a ride is 0.187
    # For 1000 drivers, we expect to see approx. 3740 rides per day, 187000 rides over 50 days.
    # Running the sim while counting the number of rides with this parameter shows that it works. 

# For those 5 million drivers, Uber claims to have 103 million average monthly users. (Source 1)
    # This means an average of 20.6 riders per driver. We will generate 20.6*1000 riders and scatter them
    # randomly about the board. 

# In 2017, 36.1 % of Uber drivers were female. (source 1)

# In 2018, Uber reported 3045 sexual assaults in 1.3 billion rides (Source 1)
    # Assuming this rate of "assaults per ride" still holds, we expect to see about 0.438 assaults in the fifty days of 
    # our simulation. Since that's absoultely tiny, we are going to scale it up by multiplying this "assaults per ride" 
    # parameter by 1000. Thus, we expect to see about 432 assaults per 50-day sim, on average. 

# The probability of an assault happening on a ride is assumed to be equal to the probability that at least one of the
# riders is malicious AND that an assault happens. The parameter to be adjusted in order to tune the model to match reality
# is the proportion of malicious people in the model. (While this joint probability is going to be 1000 times as high as 
# real life, we cannot say for certain if our model has 1000 times as many malicious people as real life.)

# In a study, 98.1% of female rape victims and 92.5% of female non-rape sex crime victims reported male perpetrators. (Source 2)
    # We will average this to say ~95% of female sexual assault victims will report male perpetrators. This means mTw ~ 19x wTw

# For male sexual assault victims, the sex of the perpetrator varied widely based on the type of violence. (ex: rape vs. groping)
    # This makes things difficult, as ultimately our preferred sex will have to come down to a guess. We have 4 unknowns, and only
    # 3 equations. 
    # Ultimately, we went with mTw = 0.95, which makes mTm=0.05, wTm=0.95, wTw=0.05

# With some calculations from the CDC estimates (Source 2), we see that the probability a victim of sexual violence is a man is 0.2626.
    # This was used with our previous guesses to calculate the true proportions of malicious people. 
    # Of malicious people, men are 76.56% and women are 23.55%.
    # Using conditional probability, we can create a formula for the proportions of men and women who are malicious. 

# We will assume the probability an assault happens on a ride with a malicious person is 0.5. 

#TESTED FOR SOLUTIONS:
    # Lowered the probability of assault: has a significant effect
    # Make sex ratio of drivers 50/50: has no effect
    # Make drivers only able to pick up same sex: has significant effect, but also many missed rides.
    # Remove and re-roll drivers after an assault: has the most significant effect
    # Banning riders: has no effect


# Source 1: http://web.archive.org/web/20210423034332/https://www.businessofapps.com/data/uber-statistics/, accessed 3 May 2021
# Source 2:  https://www.cdc.gov/violenceprevention/pdf/nisvs_report2010-a.pdf, accessed 3 May 2021


class Board:
    #ADJUSTABLE VARIABLES
    expectedRides = 187000  #AVERAGE NUMBER OF RIDES EXPECTED OVER THE COURSE OF THE SIMULATION
    expectedAssaults = 438  #AVERAGE NUMBER OF ASSAULTS EXPECTED OVER THE COURSE OF THE SIMULATION
    numDrivers = 1000       #NUMBER OF DRIVERS IN THE SIMULATION
    numDays = 50            #NUMBER OF DAYS THE SIMULATION RUNS FOR
    probMalicious = 0.005   #PROBABILITY A DRIVER OR RIDER IS MALICIOUS
    probAssault = 0.5	 #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
    assaultsPerRide = 0.002648       #AVERAGE NUMBER OF ASSAULTS PER RIDE, APPROX. 2000 TIMES REAL LIFE.
    ridersPer = 20.6             #NUMBER OF RIDERS GENERATED PER DRIVER
    mTw = 0.95                 #PROBABILITY A MALICIOUS MAN TARGETS WOMEN
    wTm = 0.95                 #PROBABILITY A MALICIOUS WOMAN TARGETS MEN
    pMM = 0.7656        #PROBABILITY A MALICIOUS PERSON IS A MAN

    def __init__(self):
        self.mTm = 1 - self.mTw              #PROBABILITY A MALICIOUS MAN TARGETS MEN
        self.wTw = 1 - self.wTm              #PROBABILITY A MALICIOUS WOMAN TERGETS WOMEN
        self.probMaliciousMan = self.probMalicious*self.pMM*2         #PROBABILITY A MAN IS MALICIOUS
        self.probMaliciousWoman = self.probMalicious*(1-self.pMM)*2   #PROBABILITY A WOMAN IS MALICIOUS
        self.setDrivers = set()       #SET OF DRIVERS IN THE SIMULATION
        self.setRiders = set()       #SET OF RIDERS IN THE SIMULATION
        self.day = 0                #GETTER FOR CURRENT DAY
        self.assaults = []          #TRACKS ASSAULTS BY DAY 
        self.rides = []             #TRACKS TOTAL RIDES BY DAY
        self.activeRiders = set()      #SET OF RIDERS WHO NEED A RIDE THAT DAY
        self.activeDrivers = set()     #SET OF DRIVERS WHO CAN STILL GIVE A RIDE THAT DAY
        self.driversToRemove = set()   #SET OF DRIVERS NOT ACTIVE AFTER EACH BATCH OF RIDES
        self.ridersNotServiced = []     #TRACKS NUMBER OF RIDERS NOT SERVICED BY DAY
        
        for i in range(self.numDrivers):                             #Generate Driveres      
            self.setDrivers.add(Driver(self))

        for i in range(int(self.ridersPer*self.numDrivers)):         #Generate riders
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
        print("simulation setup complete")


    #Runs the simulation
    def runSim(self):
        for day in range(self.numDays):
            self.assaults.append(0)
            self.rides.append(0)
            self.ridersNotServiced.append(0)
            self.day = day
            self.activeDrivers = self.setDrivers.copy()

            while (len(self.activeDrivers) > 0 and len(self.activeRiders) > 0):
                for driver in self.activeDrivers:         
                    riderToRemove = driver.giveRide(self)
                    #riderToRemove = driver.giveRideSameSex(self)
                    if (riderToRemove is None):
                        self.driversToRemove.add(driver)
                    else:
                        self.activeRiders.remove(riderToRemove)
                for driver in self.driversToRemove:
                    self.activeDrivers.remove(driver)
                self.driversToRemove.clear()
            self.ridersNotServiced[self.day] = len(self.activeRiders)
            self.activeRiders.clear()                      #Reset for next day
            self.activeDrivers.clear()
            for rider in self.setRiders:
                active = rider.nextDay()
                if (active):
                    self.activeRiders.add(rider)
            for driver in self.setDrivers:
                if (driver.needToReroll):
                    driver.reroll(self)
                driver.nextDay()

            #print("Day " + str(day + 1) + " completed")


class Driver:
    #ADJUSTABLE VARIABLES
    probMale = 0.639             #PROBABILITY THE DRIVER IS MALE
    radius = 1                  #RADIUS THE DRIVER CAN GIVE RIDES IN

    def __init__(self, board):
        self.ridesGiven = 0            #NUMBER OF RIDES GIVEN THAT DAY
        xcoord = r.uniform(0, 10)
        ycoord = r.uniform(0, 10)
        self.male = False               #INDICATES THE SEX OF THE DRIVER
        self.targetWomen = None         #IF MALICIOUS, INDICATES TARGET SEX
        self.coords = (xcoord, ycoord)  #COORDINATES OF THE DRIVER
        self.ridersInRange = set()      #SET OF THE RIDERS IN RANGE OF THE DRIVER
        self.activeInRange = []         #LIST OF ACTIVE RIDERS IN RANGE  
        self.isMalicious = False        #MALICIOUS INDICATOR
        self.needToReroll = False       #INDICATES IF NEED TO REROLL DRIVER

        if (r.random() < self.probMale):
            self.male = True
            if (r.random() < board.probMaliciousMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        else:
            self.male = False
            if (r.random() < board.probMaliciousWoman):
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


    #Resets the driver's sex and maliciousness, intended to simulate
    #removing the driver and replacing them with someone else. 
    def reroll(self, board):
        self.needToReroll = False         
        self.male = False               
        self.targetWomen = None             
        self.isMalicious = False       

        if (r.random() < self.probMale):
            self.male = True
            if (r.random() < board.probMaliciousMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        else:
            self.male = False
            if (r.random() < board.probMaliciousWoman):
                self.isMalicious = True
                if (r.random() < board.wTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        
        
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
                board.rides[board.day] = board.rides[board.day] + 1
                if (rider.isMalicious):
                    if ((self.male and not rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs     
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        rider.tempBanned = True
                    elif ((not self.male and rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        rider.tempBanned = True
                elif (self.isMalicious):
                    if ((rider.male and not self.targetWomen) and (r.random() < board.probAssault)):   #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        #self.needToReroll = True
                    elif ((not rider.male and self.targetWomen) and (r.random() < board.probAssault)): #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        #self.needToReroll = True
        return rider

    #Returns alias to rider if driver gave a ride to that rider. Only gives a ride to riders who are
    #the same sex as the driver. 
    #Returns None if the driver cannot give any more rides that day.
    def giveRideSameSex(self, board):
        rider = None
        if (len(self.activeInRange) > 0 and self.ridesGiven < 10):
            rider = self.activeInRange.pop(0)
            while (not (rider in board.activeRiders) and (not (rider is None))):
                if (len(self.activeInRange) > 0):
                    rider = self.activeInRange.pop(0)
                    if (self.male != rider.male):
                        rider = None
                else:
                    rider = None
            if (not rider is None):
                board.rides[board.day] = board.rides[board.day] + 1
                if (rider.isMalicious):
                    if ((self.male and not rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs     
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        rider.tempBanned = True
                    elif ((not self.male and rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        rider.tempBanned = True
                elif (self.isMalicious):
                    if ((rider.male and not self.targetWomen) and (r.random() < board.probAssault)):   #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        self.needToReroll = True
                    elif ((not rider.male and self.targetWomen) and (r.random() < board.probAssault)): #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                        self.needToReroll = True
        return rider

            

class Rider:
    # ADJUSTABLE VARIABLES
    probNeedRide = 0.1816             #PROBABILITY RIDER NEEDS A RIDE
    probMale = 0.5                      #PROBABILITY THE RIDER IS MALE

    def __init__(self, board, rx, ry):
        self.tempBanned = False             #INDICATES IF THE RIDER HAS BEEN TEMPORARILY BANNED
        self.male = False                   #INDICATES THE SEX OF THE RIDER
        self.needRide = False               #INDICATES IF RIDER NEEDS A RIDE THAT DAY
        self.coords = (rx, ry)              #COORDINATES OF THE RIDER
        self.targetWomen = None             #IF MALICIOUS, INDICATES PREFERRED TARGET SEX
        self.isMalicious = False            #MALICIOUSNESS INDICATOR
        if (r.random() < self.probMale):
            self.male = True
            if (r.random() < board.probMaliciousMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False
        else:
            self.male = False
            if (r.random() < board.probMaliciousWoman):
                self.isMalicious = True
                if (r.random() < board.wTw):
                    self.targetWomen = True
                else:
                    self.targetWomen = False

    #Resets the rider for the next day.
    #If the rider has been temporarily banned, they will not need a ride the next day.
    def nextDay(self):
        self.needRide = False
        if ((self.tempBanned == False) and (r.random() < self.probNeedRide)):
            self.needRide = True
        self.tempBanned = False     #Malicious rider makes a new account
        return self.needRide





        


#MAIN CODE

r.seed(1221)		#Set Seed
total_assaults = []	#List to store the total number of assaults per simulation
total_rides = []    #List to store the total number of rides per simulation
for i in range(50):	#Run 50 simulations
    b = Board()
    b.runSim()
    print("Simulation " + str(i + 1) + " complete! ")
    print("Average riders missed: " + str(sum(b.ridersNotServiced)/b.numDays))
    total_assaults.append(sum(b.assaults))
    total_rides.append(sum(b.rides))


#Print Data:
print("average rides per sim: " + str(numpy.mean(total_rides)))
print(str(total_rides))
print("mean assaults: " + str(numpy.mean(total_assaults)))
print(str(total_assaults))

# Significance tests
print("Rides test: ")
alpha = 0.05
print("Ho: mu = " + str(Board.expectedRides))
print("Ha: mu != " + str(Board.expectedRides))
print("Significance level = " + str(alpha))
s, p = scipy.stats.ttest_1samp(total_rides, Board.expectedRides, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))


print("Assaults test: ")
alpha = 0.05
print("Ho: mu = " + str(Board.expectedAssaults))
print("Ha: mu != " + str(Board.expectedAssaults))
print("Significance level = " + str(alpha))
s, p = scipy.stats.ttest_1samp(total_assaults, Board.expectedAssaults, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))



