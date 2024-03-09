#GFR dummy data generator and number-needed-to-harm calculator
#Race is a human made construct and this data is to be used to show harm caused by bias in algorithm
import pandas as pd
import numpy as np

np.random.seed(13)

num_samples = 10000
ages = np.random.randint(18, 90, size=num_samples) 
sex_factor = np.random.choice((1.0, .742), size=num_samples)
race_factor_percentage = 0.5 
race_factor = np.array([1.212 if x < race_factor_percentage else 1.0 for x in np.random.rand(num_samples)])
creatinine = np.random.uniform(0.5, 5.0, size=num_samples) #normal into the abnormal range in mg/dL, could be adjusted higher
gfr_with_rf = (175 * ((creatinine)**(-1.154))*((ages)**(-0.203))*(sex_factor)*(race_factor))
gfr_without_rf = (175 * ((creatinine)**(-1.154))*((ages)**(-0.203))*(sex_factor))

df = pd.DataFrame({
    'Age': ages,
    'Biological Sex': sex_factor,
    'Race': race_factor,
    'Creatinine': creatinine,
    'eGFR with race coefficient': gfr_with_rf,
    'eGFR without race coefficient': gfr_without_rf,
})

print(df.head(5))

cutoff = 15

def check_group_A(row): #function that checks if range contains 30
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    #return min_gfr <= 30 and max_gfr >= 30
    return min_gfr <= cutoff and max_gfr >= cutoff

df['Contains 30'] = df.apply(check_group_A, axis=1) #axis 1 scans columns, 0 does rows
exposure_with_outcome = (df['Contains 30'].sum()) #this value represents group A in NNH analysis

def check_under(row): #checks if gfr under 30, stays under 30
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    #return (min_gfr <= 30 and max_gfr <= 30)
    return (min_gfr <= cutoff and max_gfr <= cutoff)

df['Stays Under 30'] = df.apply(check_under, axis=1) 
under_30 = (df['Stays Under 30'].sum())

def check_over(row): #checks if gfr over 30, stays over 30
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    #return (min_gfr >= 30 and max_gfr >= 30)
    return (min_gfr >= cutoff and max_gfr >= cutoff)

df['Stays Over 30'] = df.apply(check_over, axis=1)
over_30 = (df['Stays Over 30'].sum())

def check_race(row):
    race_check = (row['Race'])
    return race_check == 1.000

df['Race'] = df.apply(check_race, axis=1)
no_exposure_without_outcome = (df['Race'].sum())

exposure_without_outcome = (over_30)+(under_30)-(no_exposure_without_outcome)
no_exposure_with_outcome = (0.5)

print(df.head())
print(exposure_with_outcome) #group A
#print(under_30)
#print(over_30)
print(exposure_without_outcome) #group B
print(no_exposure_with_outcome) #group C
print(no_exposure_without_outcome) #group D

exposure_event_rate = (exposure_with_outcome)/((exposure_with_outcome)+(exposure_without_outcome))
control_event_rate = (no_exposure_with_outcome)/((no_exposure_with_outcome)+(no_exposure_without_outcome))
print(exposure_event_rate)
print(control_event_rate)
attributable_risk_increase = np.abs((control_event_rate)-(exposure_event_rate))
number_needed_to_harm = 1/(attributable_risk_increase)
print(attributable_risk_increase)
print(number_needed_to_harm)















