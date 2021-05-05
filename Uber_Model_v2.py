import random as r
import math
import matplotlib.pyplot as plotter
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
    # This means an average of 20.6 riders per driver. We will give each driver 20 riders, on the argument that
    # each driver needs to have at least that many to sustain themselves.

# In 2017, 36.1 % of Uber drivers were female. (source 1)

# In the 2017-2018 period, there were 3045 sexual assaults in 2.3 billion rides (Source 1)
    # Assuming each one is a unique person, this means that ~0.00013% of users are malicious. 
    # To ensure this has a meaningful impact on our model, we are scaling this up by a factor of 20000.
    # So the probability a person is malicious in our model 0.02648. 
    # This means we expect to see ~834 assaults over the 50 days of the model, average of 16.68 per day.

# In a study, 98.1% of female rape victims and 92.5% of female non-rape sex crime victims reported male perpetrators. (Source 2)
    # We will average this to say ~95% of female sexual assault victims will report male perpetrators. This means mTw ~ 19x wTw

# For male sexual assault victims, the sex of the perpetrator varied widely based on the type of violence. (ex: rape vs. groping)
    # This makes things difficult, as ultimately our preferred sex will have to come down to a guess. We have 4 unknowns, and only
    # 3 equations. 
    # Ultimately, we went with mTw = 0.95, which makes mTm=0.05, wTm=0.95, wTw=0.05

# With some calculations from the CDC estimates (Source 2), we see that the probability a victim of sexual violence is a man is 0.2626.
    # This was used with our previous guesses to calculate the true proportions of malicious people. 
    # Of malicious people, men are 76.56% and women are 23.55%.
    # Thus, with the probability someone is malicious of 0.02648, the probability a man
    # is malicious is 0.020243 and the probability is 0.006236. (Again, this is ~20000x real life values)

# By running multiple simulations, we have determined that the probability an assault happens
# when a malicious person is on a ride is 0.3938.



# Source 1: http://web.archive.org/web/20210423034332/https://www.businessofapps.com/data/uber-statistics/, accessed 3 May 2021
# Source 2:  https://www.cdc.gov/violenceprevention/pdf/nisvs_report2010-a.pdf, accessed 3 May 2021


class Board:
    numDrivers = 1000
    numDays = 50
    
    def __init__(self):
        self.mTw = 0.95                 #PROBABILITY A MALICIOUS MAN TARGETS WOMEN
        self.mTm = 1 - self.mTw              #PROBABILITY A MALICIOUS MAN TARGETS MEN
        self.wTm = 0.95                 #PROBABILITY A MALICIOUS WOMAN TARGETS MEN
        self.wTw = 1 - self.wTm              #PROBABILITY A MALICIOUS WOMAN TERGETS WOMEN
        self.probMaliciousMan = 0.02023    #PROBABILITY A MAN IS MALICIOUS
        self.probMaliciousWoman = 0.00625  #PROBABILITY A WOMAN IS MALICIOUS
        self.probAssault = 0.345	 #PROBABILITY OF AN ASSAULT DURING A RIDE WITH A MALICIOUS PERSON
        self.setDrivers = set()       #SET OF DRIVERS IN THE SIMULATION
        self.setRiders = set()       #SET OF RIDERS IN THE SIMULATION
        self.day = 0                #GETTER FOR CURRENT DAY
        self.assaults = []          #TRACKS ASSAULTS BY DAY 
        self.rides = []             #TRACKS TOTAL RIDES BY DAY
        self.activeRiders = set()      #SET OF RIDERS WHO NEED A RIDE THAT DAY
        self.activeDrivers = set()     #SET OF DRIVERS WHO CAN STILL GIVE A RIDE THAT DAY
        self.driversToRemove = set()   #SET OF DRIVERS NOT ACTIVE AFTER EACH BATCH OF RIDES
        
        for i in range(self.numDrivers):
            Driver(self)
        
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
    ridersPer = 20              #NUMBER OF RIDERS GENERATED PER DRIVER
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

        for i in range(self.ridersPer):         #Generate 20 riders per driver
            rx = xcoord + r.uniform(-1*self.radius, self.radius)
            ybound = math.sqrt(self.radius*self.radius - (rx - xcoord)**2)
            ry = ycoord + r.uniform(-1*ybound, ybound)
            newRider = Rider(board, rx, ry)
            board.setRiders.add(newRider)
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
    def nextDay(self):
        self.needRide = False
        if (r.random() < self.probNeedRide):
            self.needRide = True
        return self.needRide





        


#MAIN CODE

r.seed(1212)		#Set Seed
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
alpha = 0.05
print("Ho: mu = 834")
print("Ha: mu != 834")
print("Significance level = " + str(alpha))
s, p = scipy.stats.ttest_1samp(total_assaults, 834.0, alternative="two-sided")
print("P_value = " + str(p))
print("Reject Ho = " + str((p < alpha)))




