# Uber_Statistical_Model

This project aims to build a mathematical simulation model of a rideshare service with riders and drivers in a relatively densely populated city. The goal is to track the number of sexual assaults that occur and see what effects certain policy changes have, i.e. giving riders the ability to indicate a preferred gender of driver. 

The statistics used in this model are based off of Uber, simply because they have the most readily available data.

Author: Ian Roberts

Last Updated: 23 June 2022

## Files:

- README.md - the README file for this project.

- LICENSE - This project is under the MIT license. Copying, distributing, and making derivative works from this project is allowed and encouraged for the benefit of scientific progress. 

- Uber_Model_rough_draft.py - the first build of a simple riders/drivers simulation with some malicious users. Does not include sex of the service's users, and was intended more as an early prototype. *This model will not be used to draw any conclusions on the change in sexual assaults.*

- Uber_Model_baseline.py - this iteration introduces the sex of each driver and rider, as well as malicious users having a preferred target sex. This version is intended to match reality; it includes several comments justifying the values of the various parameters in the simulation, as well as a student's t-test to ensure the average number of sexual assaults and rides from the simulation are close enough to the expected numbers. *This is the model that is meant to best match reality.*

- Uber_Model_choice_test.py - this iteration introduces the ability for riders to indicate a preferred sex for each driver. The purpose of this is to test what effect this change will have on the average number of sexual assaults over the simulation. Includes a student's t-test to ensure the average number of rides is close enough to the expected number, and another to determine if the change causes a change in the number of sexual assaults. *This is the model that is meant to test what happens when riders are given the option to indicate a preferred driver sex.*

- Further Tests - this folder contains the code for models that test what other factors may impact the number of sexual assaults on rideshare platforms. Each was made by copying the Uber_Model_baseline.py file and making the necessary adjustments. The README file inside this folder describes what each file in the folder is testing. 

- the_main_runs.txt - this file includes the final console output for all of the tests that appear in the final report. This is every Uber_Model_* file that appears in this repository except for Uber_Model_rough_draft. This is meant to be a log of the data I saw on my computer. 

## RUNNING THE SIMULATION

This simulation is written in Python 3. Make sure you have the Python 3 interpreter to run it.

Ensure you have the correct libraries installed. This project requires Python's "math", "random", "numpy", and "scipy" libraries. If you are missing any of these, run the following command in your terminal:

> pip3 install [package name]

To run any of the simulations, use the following command:

> python3 \[filename\]

For example:

> python3 Uber_model_baseline.py

replacing the "#" with the number of the model you wish to run. 


## HOW THE MODEL WORKS:

1000 drivers are randomly placed on a 10x10 coordinate grid. Then, for each driver, an average of 22.2 riders are randomly scattered around the board. (There is significant overlap between the drivers that can service each rider.) 

Each "day" in the simulation, some portion of the riders will want a ride. One of the drivers within a radius of 1 unit of the rider will service that request. (Each driver can service up to 10 riders per day. The order they service riders in changes each day.) Some percentage of drivers and riders will be "malicious"\*. If either the driver or the rider is malicious (or both) and they are riding with a preferred target, there is a chance an assault will occur. (This will not happen 100% of the time, partly because that's what will happen realistically.) If an assault occurs, that rider and driver will never ride with each other again. 

Once all riders have been serviced or no drivers are left to service those still available, the day ends and the next day is set up, with a new selection of riders needing rides. The simulation  runs for 50 days and tracks the number of sexual assaults that occur each day and the number of rides that occur each day.

In the model rough draft, preferred targets were not implemented; if a malicious person was on a ride, an assault always had a chance of occurring. The baseline model introduced sexes. Each user is either male or female, and each malicious person has a preferred target sex. An assault only has a chance of happening if a malicious person rides with someone they consider a preferred target. (ex: if a malicious man targets other men, but rides with a woman, an assault will not happen.) 

The choice test model implements rider choice. Riders can indicate a preference for either male or female drivers, which is determined when the rider is initialized. Some proportion of users, both malicious and non-malicious, will utilize this function. A driver will not pick up someone who indicates a different preferred driver sex unless there is nobody else in range that they can give a ride to. (i.e. if a male driver sees 2 riders who prefer female drivers and 1 user with no preference, they will pick up the user with no preference. If, instead, he saw 3 riders who prefer female drivers, he would just pick one of them up regardless.) This is under the assumption that a driver will focus on making money by giving rides, and will disregard the preference if there are no other options. 

\* "malicious" in this context only refers to an agent's ability to commit sexual assault.

## POTENTIAL PROBLEMS WITH THE MODEL:

- Malicious users will never again ride with someone they have assaulted, and the simulation never adds new people. Thus, the number of assaults drops sharply (and unrealistically) if the simulation runs for long enough. To account for this, the tests we ran with this simulation only run for 50 days, where this effect is negligible. 

- With 1000 drivers, we expect the model to proportionally give 172200 rides in its 50 simulated days. Using the real-world values of assaults per ride (3045 in 1.3 billion rides), we would expect 0.403 assaults in the expected 172200 rides, which is too small to notice any effect. In order to combat this, the model is tuned to give us 1000 times as many assaults as in real life - about 403 on average - by increasing the number of malicious people and the probability a ride with a malicious person ends in an assault. This should not be an issue, as we are only examining the deviation from the baseline, so this artificial scaling should not impact the final results. 

- We assumed that drivers - even malicious drivers - do not make intentional decisions about who to give a ride to. The reasoning for this is that drivers need to make sufficient money by giving rides, and that they would not let personal feelings get in the way of that. In reality, people are complex and irrational, and it's possible malicious drivers could choose to pick up someone they consider a target despite economic incentive. Plus, in any system, it's possible for a rideshare company to control who a driver sees. 

- While the proportions of malicious men/women that target each sex are interrelated, they were ultimately based on an estimation. By extension, the proportion of men who are malicious and the proportion of women who are malicious in our model were calculated based off of that guess. 

- In the rider_choice model, when riders can choose to indicate a preferred driver sex, there is no data for what proportion of people would indicate a preference or how many would choose which driver sex. The numbers in the model are pure guesswork, based on an assumption that non-malicious men would not be as safety-concious and would be less likely to indicate a preference, as well as relatively equally preferring men and women. By contrast, we assume non-malicious women are more safety concious and are more likely to indicate a female driver. Ultimately, however, playing around with these numbers only caused minor changes to the final assault average. 


## RESULTS

For 1000 drivers in a 50-day simulation, we expect a total of 172200 rides and 403.3 sexual assaults. 

In the baseline model, with random table seed set to 2112 and the proportion of malicious people being 0.005, we see an average of 172184.86 rides and 408.28 assaults per 50-day simulation. This is close enough to the expected values that we can say the baseline model matches reality. Then, running the choice test model, we got averages of 172265.8 rides and 453.6 assaults per simulation. The number of rides lines up, but the number of assaults increased. Our student's t-test on the average number of assaults at the end of the simulation rejects its null hypothesis, so this difference is statistically significant.

Thus, we conclude that allowing Uber riders to choose the sex of their driver will - counterintuitively - *increase* the number of sexual assaults. By extention, it is reasonable to assume this applies to all rideshare services which have a mixed-sex target demographic. (i.e. this result should *not* be used to draw conclusions about women-only rideshare services.)

Other alternative approaches were tested, and can be found in the further tests folder. 

From all of those tests, we can conclude that the best approaches to successfully reducing sexual assaults on rideshare services line up with traditional wisdom. Gender segregation does work, but if that is too difficult, then the best options are to have accountability for drivers first and safety measures on rides second. 

## SOURCES

- https://www.reddit.com/r/AskWomen/comments/mivewb/what_do_you_think_about_having_the_option_to/
  - The post that inspired this project.

- http://web.archive.org/web/20210423034332/https://www.businessofapps.com/data/uber-statistics/, accessed 3 May 2021
  - Statistics on the use of Uber and their safety report, used to estimate several model parameters.

- https://www.cdc.gov/violenceprevention/pdf/nisvs_report2010-a.pdf, accessed 3 May 2021
  - A report on sexual assault including statistics around victims and perpetrators, used to calculate the proportion of men and women who are "malicious" in the model. 
