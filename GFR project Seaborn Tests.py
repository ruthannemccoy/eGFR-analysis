#Dummy data generator, absolute risk increase, and number-needed-to-harm calculator
#Race is a human made construct and this program is to be used to investigate harm caused by the eGFR race adjustment

#Libraries used
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy as sp
from scipy.stats import beta

#Parameters for creation of dummy data
np.random.seed(13)
num_samples = 10000
a, b = 2, 5
ages = 18 + (beta.rvs(a, b, size=num_samples) * (90 - 18))
ages = np.round(ages).astype(int)
sex_factor = np.random.choice((1.0, .742), size=num_samples)
race_factor_percentage = 0.1 
race_factor = np.array([1.212 if x < race_factor_percentage else 1.0 for x in np.random.rand(num_samples)])
creatinine = np.random.uniform(0.5, 10.0, size=num_samples) #normal into the abnormal range in mg/dL, could be adjusted higher
gfr_with_rf = (175 * ((creatinine)**(-1.154))*((ages)**(-0.203))*(sex_factor)*(race_factor))
gfr_without_rf = (175 * ((creatinine)**(-1.154))*((ages)**(-0.203))*(sex_factor))

#Dataframes set up with pandas
df = pd.DataFrame({
    'Age': ages,
    'Biological Sex': sex_factor,
    'Race': race_factor,
    'Creatinine': creatinine,
    'eGFR with race coefficient': gfr_with_rf,
    'eGFR without race coefficient': gfr_without_rf,
})

#Age distribution plot
# sns.set_style('whitegrid')
# plt.figure(figsize=(10, 6))
# sns.histplot(df['Age'], bins=30, kde=True, color='blue')
# plt.title('Age Distribution')
# plt.xlabel('Age')
# plt.ylabel('Frequency')
# plt.show()

#Functions to sort subjects into groups for the analysis
cutoff = 30 #cutoff for nephrology consult
def check_group_A(row): #function that checks if range contains cutoff
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    return min_gfr <= cutoff and max_gfr >= cutoff
df['Contains 30'] = df.apply(check_group_A, axis=1) #axis 1 scans columns, 0 does rows
exposure_with_outcome = (df['Contains 30'].sum()) #this value represents group A in NNH analysis
def check_under(row): #checks if gfr under cutoff, stays under cutoff
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    return (min_gfr <= cutoff and max_gfr <= cutoff)
df['Stays Under 30'] = df.apply(check_under, axis=1) 
under_30 = (df['Stays Under 30'].sum())
def check_over(row): #checks if gfr over cutoff, stays over cutoff
    min_gfr = min(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    max_gfr = max(row['eGFR with race coefficient'], row['eGFR without race coefficient'])
    return (min_gfr >= cutoff and max_gfr >= cutoff)
df['Stays Over 30'] = df.apply(check_over, axis=1)
over_30 = (df['Stays Over 30'].sum())
def check_race(row): #checks if subject is not Black and therefore unexposed and unaffected
    race_check = (row['Race'])
    return race_check == 1.000
df['Race'] = df.apply(check_race, axis=1)
no_exposure_without_outcome = (df['Race'].sum()) #group D
exposure_without_outcome = (over_30)+(under_30)-(no_exposure_without_outcome) #group B
no_exposure_with_outcome = (0.5) #small value for group C, which is technically zero, to avoid null value

print(df[['Age', 'Biological Sex', 'Race', 'Creatinine', 'eGFR without race coefficient', 'eGFR with race coefficient', 'Contains 30']].head(10))
print(exposure_with_outcome) #group A
print(exposure_without_outcome) #group B
print(no_exposure_with_outcome) #group C
print(no_exposure_without_outcome) #group D

#Truth table
# truth_table_data = {'':['Exposed','Unexposed'], 'Outcome Met':[exposure_with_outcome, no_exposure_with_outcome], 'Outcome Not Met': [exposure_without_outcome, no_exposure_without_outcome]}
# df2 = pd.DataFrame(truth_table_data)
# fig, ax = plt.subplots(figsize=(8,8))
# ax.axis('tight')
# ax.axis('off')
# truth_table_fig = ax.table(cellText=df2.values, colLabels=df2.columns, loc='center', cellLoc='center', fontsize=12)
# plt.savefig('table.png', dpi=300)
# plt.show()

#Equations to calculate epidemioloically meaningful values including NNH
exposure_event_rate = (exposure_with_outcome)/((exposure_with_outcome)+(exposure_without_outcome))
control_event_rate = (no_exposure_with_outcome)/((no_exposure_with_outcome)+(no_exposure_without_outcome))
absolute_risk_increase = np.abs((control_event_rate)-(exposure_event_rate))
number_needed_to_harm = 1/(absolute_risk_increase)

print(exposure_event_rate)
print(control_event_rate)
print(absolute_risk_increase)
print(number_needed_to_harm)
















