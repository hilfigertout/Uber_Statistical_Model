# Uber_Statisical_Model

This project aims to build a mathematical simulation model of a rideshare service with riders and drivers in a relatively densely populated city. The goal is to track the number of sexual assaults that occur and see what effects certain policy changes have, i.e. giving riders the ability to indicate a preferred gender of driver. 

The statistics used in this model are based off of Uber, simply because they have the most readily available data.

## Files:

- README.md - the README file for this project.

- LICENSE - This project is under the MIT license. Copying, distributing, and making derivative works from this project is allowed and encouraged for the benefit of scientific progress. 

- Uber_Model_v1.py - the first build of a simple riders/drivers simulation with some malicious users. Does not include sex of the service's users, and was intended more as an early prototype. *This model will not be used to draw any conclusions on the change in sexual assaults.*

- Uber_Model_v2.py - this iteration introduces the sex of each driver and rider, as well as malicious users having a preferred target sex. This version is intended to match reality; it includes several comments justifying the values of the various parameters in the simulation, as well as a student's t-test to ensure the average number of sexual assaults and rides from the simulation are close enough to the expected numbers. *This is the model that is meant to best match reality.*

- Uber_Model_v3.py - this iteration introduces the ability for riders to indicate a preferred sex for each driver. The purpose of this is to test what effect this change will have on the average number of sexual assaults over the simulation. Includes a student's t-test to ensure the average number of rides is close enough to the expected number, and another to determine if the change causes a change in the number of sexual assaults. *This is the model that is meant to test our hypothesis.*


## RUNNING THE SIMULATION

This simulation is written in Python 3. Make sure you have the Python 3 interpreter to run it.

Ensure you have the correct libraries installed. This project requires python's "math" and "random" libraries for all three simulations. Models v2 and v3 also require "numpy" and "scipy". If you are missing any of these, run the following command in the command prompt:

> pip3 install [package name]

To run any of the simulations, use the following command:

> python3 Uber_Model_v#.py

replacing the "#" with the number of the model you wish to run. 


## HOW THE MODEL WORKS:

1000 drivers are randomly placed on a 10x10 coordinate grid. In a 1 unit radius around each driver, 20 riders are randomly placed. (There is significant overlap between the drivers that can service each rider.) Note that this means some riders can be outside the 10x10 grid, which we will interpret as being on the outskirts of our city. 

Each "day" in the simulation, some portion of the riders will want a ride. One of the drivers within a radius of 1 unit of the rider will service that request. (Each driver can service up to 10 riders per day. The order they service riders in changes each day.) Some percentage of drivers and riders will be malicious. If either the driver or the rider is malicious (or both) and they are riding with a preferred target, there is a chance an assault will occur. (This will not happen 100% of the time, partly because that's what will happen realistically and partly because it gives us a simple parameter to tweak to ensure the simulation matches reality.) If an assault occurs, that rider and driver will never ride with each other again. 

Once all riders have been serviced or no drivers are left to service those still available, the day ends and the next day is set up, with a new selection of riders needing rides. The simulation  runs for 50 days and tracks the number of sexual assaults that occur each day and the number of rides that occur each day.

In model v1, preferred targets were not implemented; if a malicious person was on a ride, an assault always had a chance of occurring. Model v2 introduced sexes. Each user is either male or female, and each malicious person has a preferred target sex. An assault only has a chance of happening if a malicious person rides with someone they consider a preferred target. (ex: if a malicious man targets other men, but rides with a woman, an assault will never happen.) 

Model v3 implements rider choice. Riders can indicate a preference for either male or female drivers, which is determined when the rider is initialized. All malicious users and some proportion of non-malicious users will utilize this function. A driver will not pick up someone who indicates a different preferred driver sex unless there is nobody else in range that they can give a ride to. (i.e. if a male driver sees 2 riders who prefer female drivers and 1 user with no preference, they will pick up the user with no preference. If, instead, he saw 3 riders who prefer female drivers, he would just pick one of them up regardless.) This is under the assumption that a driver will focus on making money by giving rides, and will disregard the preference if there are no other options. 

## POTENTIAL PROBLEMS WITH THE MODEL:

- Malicious users will never again ride with someone they have assaulted, and the simulation never adds new people. Thus, the number of assaults drops sharply (and unrealistically) if the simulation runs for long enough. To account for this, the simulation only runs for 50 days, where this effect is negligible. 

- We multiplied the proportion of malicious people by 20,000 in order to get usable data, and we assumed that this meant that there would be 20,000 times as many sexual assaults as in reality. This assumption that the number of sexual assaults scales linearly with the proportion of malicious people may not be entirely accurate, and we do not have any mathematical or statistical proof of it. 

- We assumed that drivers - even malicious drivers - do not make intentional decisions about who to give a ride to. The reasoning for this is that drivers need to make sufficient money by giving rides, and that they would not let personal feelings get in the way of that. In reality, people are complex and irrational, and it's possible malicious drivers could choose to pick up someone they consider a target. 

- While the proportions of malicious men/women that target each sex are interrelated, they were ultimately based on an estimation. By extension, the proportion of men who are malicious and the proportion of women who are malicious in our model were calculated based off of that guess. 

- In model v3, when riders can choose to indicate a preferred driver sex, there is no data for what proportion of people would indicate a preference or how many would choose which driver sex. The numbers in the model are pure guesswork, based on an assumption that non-malicious men would not be as safety-concious and would be less likely to indicate a preference, as well as relatively equally preferring men and women. By contrast, we assume non-malicious women are more safety concious and are more likely to indicate a female driver. Ultimately, however, playing around with these numbers only caused minor changes to the final assault average. 

- We assumed that 100% of all malicious riders in model v3 utilize the driver choice feature to bring targets to them. In reality, some may instead be opportunistic predators instead of premeditated ones. Additionally, we assumed the average chance of an assault happening did not change from model v2 to model v3. It is possible that having a perpetrator that is already bringing targets to them could increase the likelihood of an assault occurring, since it's premeditated.

## SOURCES


- https://www.reddit.com/r/AskWomen/comments/mivewb/what_do_you_think_about_having_the_option_to/
- - The post that inspired this project.

- http://web.archive.org/web/20210423034332/https://www.businessofapps.com/data/uber-statistics/, accessed 3 May 2021
- - Statistics on the use of Uber and their safety report.

- https://www.cdc.gov/violenceprevention/pdf/nisvs_report2010-a.pdf, accessed 3 May 2021
- - A report on sexual assault including statistics around victims and perpetrators. 