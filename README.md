# Uber_Statisical_Model

This project aims to build a mathematical simulation model of a rideshare service with riders and drivers in a relatively densely populated city. The goal is to track the number of sexual assaults that occur and see what effects certain policy changes have, i.e. giving riders the ability to indicate a preferred gender of driver. 

## Files:

Uber_Model_v1.py - the first build of a simple riders/drivers simulation with some malicious users. Does not include sex of the service's users, and was intended more as an early proof of concept.

Uber_Model_v2.py - this iteration introduces the sex of each driver and rider, as well as malicious users having a preferred target sex. This version is intended to match reality; it includes several comments justifying the values of the various parameters in the simulation, as well as a student's t-test to ensure the average number of sexual assaults from the simulation is close enough to the expected number. 

Uber_Model_v3.py - this iteration introduces the ability for riders to indicate a preferred sex for each driver. The purpose of this is to test what effect this change will have on the average number of sexual assaults over the simulation. 


## HOW THE MODEL WORKS:

1000 drivers are randomly placed on a 10x10 coordinate grid. In a 1 unit radius around each driver, 20 riders are randomly placed. (There is significant overlap between the drivers that can service each rider.) Note that this means some riders can be outside the 10x10 grid, which we will interpret as being on the outskirts of our city. 

Each "day" in the simulation, some portion of the riders will want a ride. One of the drivers within a radius of 1 unit of the rider will service that request. (Each driver can service up to 10 riders per day. The order they service riders in changes each day.) Some percentage of drivers and riders will be malicious. If either the driver or the rider is malicious (or both) and they are riding with a preferred target, there is a chance an assault will occur. (This will not happen 100% of the time, partly because that's what will happen realistically and partly because it gives us a simple parameter to tweak to ensure the simulation matches reality.) If an assault occurs, that rider and driver will never ride with each other again. 

Once all riders have been serviced or no drivers are left to service those still available, the day ends and the next day is set up, with a new selection of riders needing rides. The simulation  runs for 50 days and tracks the number of sexual assaults that occur each day and the number of rides that occur each day.

## PROBLEMS WITH THE MODEL:

- Malicious users will never again ride with someone they have assaulted, and the simulation never adds new people. Thus, the number of assaults drops sharply (and unrealistically) if the simulation runs for long enough. To account for this, the simulation only runs for 50 days, where this effect is negligible. 