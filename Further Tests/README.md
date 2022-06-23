# Uber Statistical Model

## Further Tests

This folder contains files meant to test what parameters change the number of sexual assaults on rideshare platforms *other than* allowing riders to choose the sex of their drivers. (That one was the inspiration and main goal of this project, these are secondary.)

## Files

- Uber_Model_safety_test.py - this model tests the effectiveness of measures designed to reduce the probability of an assault on a ride with a malicious person. This can be done in the real world with safety measures such as barriers or cameras in the car. This model resulted in a statistically significant decrease in the number of assaults. 

- Uber_Model_more_women_drivers.py - this model tests the effectiveness of increasing the number of women who drive for rideshare services. One run with 50% female drivers resulted in a statistically significant increase in the number of assaults. Another run with 100% female drivers resulted in no significant change to the number of assaults. 

- Uber_Model_sex_segregation.py - this model forces drivers to only pick up riders of the same sex. This resulted in a statistically significant decrease in the number of assaults. 

- Uber_Model_driver_accountability.py - this model removes a driver who commits an assault after a set number of days to simulate holding malicious drivers accountable. This was tested three tiems, with drivers being removed 1 day after an assault, 3 days after an assault, and 10 days after an assault respectively. All three tests resulted in a statistically significant decrease in the number of sexual assaults. 

- Uber_Model_rider_accountability.py - this model removes a rider who commits an assault from the app after a set number of days. However, it is assumed that malicious riders will go on to make a new account after a time, so riders return after a set number of days. This was tested three times: once with riders removed one day after an assault and returning one day later, once with riders removed three days after an assault and replaced three days later, and once with riders removed five days after an assault and replaced five days later. None of these tests resulted in a statistically significant change in the number of sexual assaults. 

- Uber_Model_opt-out_segregation.py - this model tests a novel solution in which the default for riders is for only drivers of the same sex to pick them up. However, it is possible for riders to indicate that they will be ok with drivers of either sex picking them up. It was assumed that 30% of non-malicious male riders and 70% of non-malicious female riders would stay segregated, and the rest would opt-out. Malicious users would choose based on whether they target their own sex or the opposite sex. This test resulted in a statistically significant decrease in the number of sexual assaults. 