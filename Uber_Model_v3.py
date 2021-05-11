import random as r
import math
#import matplotlib.pyplot as plotter
import numpy
import scipy
from scipy import stats

# Rideshare service simulation model that includes rider choice
# Author: Ian Roberts

# SOURCES AND DERIVATIONS FROM V2: 

# In 2019 and 2020, there were 5 million Uber drivers and 18.7 million trips per day, on average. (Source 1)
    # This means that each driver makes an average of 3.74 trips per day. So for a minimum of 20 riders per driver,
    # we will say the probability a rider needs a ride is 0.187
    # For 1000 drivers, we expect to see approx. 3740 rides per day, 187000 rides over 50 days.
    # Running the sim while counting the number of rides with this parameter shows that it works. 

# For those 5 million drivers, Uber claims to have 103 million average monthly users. (Source 1)
    # This means an average of 20.6 riders per driver. We will give each driver 20 riders, on the argument that
    # each driver needs to have at least that many to sustain themselves.

# In 2017, 36.1 % of Uber drivers were female. (source 1)

# In the 2017-2018 period, there were 3045 sexual assaults in 2.3 billion rides (Source 1)
    # Assuming each one is a unique person, this means that of the 108 million people ~0.0028% of them are malicious. 
    # To ensure this has a meaningful impact on our model, we are scaling this up by a factor of 1000.
    # So the probability a person is malicious in our model 0.02819.
    # 
    # ???????? 
    # All told, with 1000 times more assaults than real life, we expect to see ~42 assaults over 
    # the 50 days of the model.

# In a study, 98.1% of female rape victims and 92.5% of female non-rape sex crime victims reported male perpetrators. (Source 2)
    # We will average this to say ~95% of female sexual assault victims will report male perpetrators. This means mTw ~ 19x wTw

# For male sexual assault victims, the sex of the perpetrator varied widely based on the type of violence. (ex: rape vs. groping)
    # This makes things difficult, as ultimately our preferred sex will have to come down to a guess. We have 4 unknowns, and only
    # 3 equations. 
    # Ultimately, we went with mTw = 0.95, which makes mTm=0.05, wTm=0.95, wTw=0.05

# With some calculations from the CDC estimates (Source 2), we see that the probability a victim of sexual violence is a man is 0.2626.
    # This was used with our previous guesses to calculate the true proportions of malicious people. 
    # Of malicious people, men are 76.56% and women are 23.55%.
    # Thus, with the probability someone is malicious of 0.02648, the probability someone is malicious given that
    # they are a man is 0.0405, and the probability someone is malicious given that they are a woman is 0.0139
    # (Again, this is ~20000x real life values)

# By running multiple simulations, we have determined that the probability an assault happens
# when a malicious person is on a ride is 0.3938.

# NEW ADDITIONS

# When a rider needs a ride, they may indicate a preferred sex. If the driver is not that sex, then
# the driver will not give them a ride unless nobody else is available. 

# 40% of non-malicious male riders will indicate a preferred sex; 50% of the time it will be women 
# and 50% of the time it will be men. 
# 60% of non-malicious female riders will indicate a preferred sex; 80% of the time it will be
# women, and 20% of the time it will be men. 
#       These numbers are sheer guesswork, under the assumption that men do not feel the same safety concerns
#       as women are are less likely to care who picks them up. 

# Source 1: http://web.archive.org/web/20210423034332/https://www.businessofapps.com/data/uber-statistics/, accessed 3 May 2021
# Source 2:  https://www.cdc.gov/violenceprevention/pdf/nisvs_report2010-a.pdf, accessed 3 May 2021


class Board:
    numDrivers = 1000
    numDays = 50
    
    def __init__(self):
        self.ridersPer = 20.6            #NUMBER OF RIDERS GENERATED PER DRIVER
        self.mPreference = 0.4          #PROBABILITY A NON-MALICIOUS MAN HAS A PREFERRED DRIVER SEX
        self.mPw = 0.5                  #PROBABILITY A NON-MALICIOUS MAN PREFERS FEMALE DRIVERS
        self.wPreference = 0.6         #PROBABILITY A WOMAN HAS A PREFERRED DRIVER SEX
        self.wPw = 0.8                  #PROBABILITY A NON-MALICIOUS WOMAN PREFERS FEMALE DRIVERS
        self.mTw = 0.95                 #PROBABILITY A MALICIOUS MAN TARGETS WOMEN
        self.mTm = 1 - self.mTw              #PROBABILITY A MALICIOUS MAN TARGETS MEN
        self.wTm = 0.95                 #PROBABILITY A MALICIOUS WOMAN TARGETS MEN
        self.wTw = 1 - self.wTm              #PROBABILITY A MALICIOUS WOMAN TERGETS WOMEN
        self.probMaliciousMan = 0.0405    #PROBABILITY A MAN IS MALICIOUS
        self.probMaliciousWoman = 0.0139  #PROBABILITY A WOMAN IS MALICIOUS
        self.probAssault = 0.345	 #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
        self.setDrivers = set()       #SET OF DRIVERS IN THE SIMULATION
        self.setRiders = set()       #SET OF RIDERS IN THE SIMULATION
        self.day = 0                #GETTER FOR CURRENT DAY
        self.assaults = []          #TRACKS ASSAULTS BY DAY 
        self.rides = []             #TRACKS TOTAL RIDES BY DAY
        self.activeRiders = set()      #SET OF RIDERS WHO NEED A RIDE THAT DAY
        self.activeDrivers = set()     #SET OF DRIVERS WHO CAN STILL GIVE A RIDE THAT DAY
        self.driversToRemove = set()   #SET OF DRIVERS NOT ACTIVE AFTER EACH BATCH OF RIDES
        
        for i in range(self.numDrivers):            #Generate drivers
            self.setDrivers.add(Driver(self))

        for i in range(int(self.ridersPer*self.numDrivers)):         #Generate 20 riders per driver
            rx = r.uniform(0, 10)
            ry = r.uniform(0, 10)
            self.setRiders.add(Rider(self, rx, ry))

        for driver in (self.setDrivers):                #Each driver finds the riders in their range
            driver.findRidersInRange(self)

        for rider in self.setRiders:                    #Set up riders and drivers for first day
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
        self.isMalicious = False       #MALICIOUS INDICATOR

        board.setDrivers.add(self)
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
        
        
    #Returns alias to rider if driver gave a ride to that rider.
    #Returns None if the driver cannot give any more rides that day.
    def giveRide(self, board):
        rider = None
        if (len(self.activeInRange) > 0 and self.ridesGiven < 10):
            i = 0                       #Tracks the number of riders who prefer a different sex than the driver.
            foundRider = False 
            noRiders = False
            while (not foundRider and not noRiders):
                if (len(self.activeInRange) > 0):
                    rider = self.activeInRange.pop(0)
                    if (rider.needRide):   #Need to check here, in case other driver already got him/her.
                        if ((i < len(self.activeInRange)) and (not rider.preferDriver(self))):
                            self.activeInRange.append(rider)
                            i = i + 1
                        else:           #Either a compatible match, or no other riders are compatible. 
                            foundRider = True
                else:
                    rider = None
                    noRiders = True 
            if (not rider is None):
                board.rides[board.day] = board.rides[board.day] + 1
                rider.needRide = False
                if (rider.isMalicious):
                    if ((self.male and not rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs     
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                    elif ((not self.male and rider.targetWomen) and (r.random() < board.probAssault)):  #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                elif (self.isMalicious):
                    if ((rider.male and not self.targetWomen) and (r.random() < board.probAssault)):   #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
                    elif ((not rider.male and self.targetWomen) and (r.random() < board.probAssault)): #Assault occurs
                        board.assaults[board.day] = board.assaults[board.day] + 1
                        self.ridersInRange.remove(rider)
        return rider


            

class Rider:
    probNeedRide = 0.187               #PROBABILITY RIDER NEEDS A RIDE
    probMale = 0.5                      #PROBABILITY THE RIDER IS MALE
    def __init__(self, board, rx, ry):
        self.male = False                   #INDICATES THE SEX OF THE RIDER
        self.needRide = False               #INDICATES IF RIDER NEEDS A RIDE THAT DAY
        self.coords = (rx, ry)              #COORDINATES OF THE RIDER
        self.isMalicious = False            #MALICIOUSNESS INDICATOR
        self.targetWomen = None             #IF MAILICIOUS, INDICATES PREFERRED TARGET SEX
        self.preferredSex = None            #IF NOT MALICIOUS, RIDER'S PREFERRED DRIVER SEX
        if (r.random() < self.probMale):
            self.male = True
            
            if (r.random() < board.probMaliciousMan):
                self.isMalicious = True
                if (r.random() < board.mTw):
                    self.targetWomen = True
                    self.preferredSex = "F"
                else:
                    self.targetWomen = False
                    self.preferredSex = "M"
            else:
                if (r.random() < board.mPreference):
                    if (r.random() < board.mPw):
                        self.preferredSex = "M"
                    else:
                        self.preferredSex="F"
        else:
            self.male = False
            if (r.random() < board.probMaliciousWoman):
                self.isMalicious = True
                if (r.random() < board.wTw):
                    self.targetWomen = True
                    self.preferredSex = "F"
                else:
                    self.targetWomen = False
                    self.preferredSex = "M"

    #Resets the rider for the next day.
    def nextDay(self):
        self.needRide = False
        if (r.random() < self.probNeedRide):
            self.needRide = True
        return self.needRide

    #Returns TRUE if the driver's sex is the same as the rider's preferred sex,
    #False otherwise.
    #If the rider has no preference, this just returns true.
    def preferDriver(self, driver):
        output = True
        if (not (self.preferredSex is None)):
            if ((driver.male and self.preferredSex == "F") or ((not driver.male) and self.preferredSex == "M")):
                output = False
        return output





        


#MAIN CODE

r.seed(2112)		#Set Seed
# b = Board()
# b.runSim()
# print("Assaults: " + str(sum(b.assaults)))
# print("Rides: " + str(sum(b.rides)))

total_assaults = []	#List to store the total number of assaults per simulation
total_rides = []    #List to store the total number of rides per simulation
for i in range(50):	#Run 50 simulations
    b = Board()
    b.runSim()
    print("Simulation " + str(i) + " complete! ")
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
print("Ho: mu = 187000")
print("Ha: mu != 187000")
print("Significance level = " + str(alpha))
s, p = scipy.stats.ttest_1samp(total_rides, 187000.0, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))


print("Assaults test: ")
alpha = 0.01
print("Ho: mu = 834")
print("Ha: mu != 834")
print("Significance level = " + str(alpha))
s, p = scipy.stats.ttest_1samp(total_assaults, 834.0, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))




