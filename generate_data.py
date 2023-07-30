import pandas as pd
import numpy as np
import random
from random import randrange
from datetime import datetime
from datetime import timedelta
from itertools import repeat

######################
### Parameters
#####################
number_patients = 10**6
interval_start = '1/1/2021'
interval_end = '31/12/2021'
variant_type = ['G6','K0','L8','M5','W3','Y6','J9']
number_waves = 4
######################

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days)
    random_days = randrange(int_delta)
    return start + timedelta(days=random_days)

# Regions
regions = pd.read_excel("NUTS2021.xlsx", sheet_name='NUTS & SR 2021')
regions['Country'] = regions['Country'].fillna(method='ffill')
regions = regions[['Country','NUTS level 2']].fillna(method='ffill').dropna().drop_duplicates().reset_index(drop = True)

regions = regions.iloc[
    np.where(regions[['NUTS level 2']]!='Extra-Regio NUTS 2')[0]
                  ]
regions = regions.reset_index(drop = True)
regions.rename(columns = {'NUTS level 2':'Region','Country':'State'}, inplace = True)

# ID patients with covid
N = list(range(1,number_patients+1))

# Boolean for ICU admission
icu_percentage = random.choices(range(1,10), k = 2)
icuadmitted = random.choices([1, 0], weights=[icu_percentage[0], icu_percentage[1]], k=int(len(N)/(number_waves*4)))
n = 20
for i in range(1,number_waves*4):
    new_icu = random.choices(range(1,n), k = 1)
    icu_percentage = np.add(icu_percentage,np.array([new_icu[0],n-new_icu[0]]))
    icuadmitted = np.append(icuadmitted,random.choices([1, 0], weights=[icu_percentage[0], icu_percentage[1]], k=int(len(N)/(number_waves*4))))
    n = n*2


# Dates for ICU admission
d1 = datetime.strptime(interval_start, '%d/%m/%Y')
d2 = datetime.strptime(interval_end, '%d/%m/%Y')

date_icu = []
for i in range(len(N)):
    date_icu.append(random_date(d1,d2))

date_icu.sort()

# Boolean for deceased
death_percentage = random.choices(range(1,10), k = 2)
deceased = random.choices([1, 0], weights=[death_percentage[0], death_percentage[1]], k=int(len(N)/(number_waves*2)))
for i in range(1,number_waves*2):
    death_percentage = np.add(death_percentage,random.choices(range(1,10), k = 2))
    deceased = np.append(deceased,random.choices([1, 0], weights=[death_percentage[0], death_percentage[1]], k=int(len(N)/(number_waves*2))))
deceased = list(np.array(deceased) * np.array(icuadmitted))


# Date deceased
def dead(t):
    k = random.choices(range(1,50))
    t = t + timedelta(days = k[0])
    return t
date_dead = list(map(dead, date_icu))

# Variants
viral_intensity = random.choices(range(1,100), k = len(variant_type))
variants = random.choices(variant_type, weights=viral_intensity, k=int(len(N)/number_waves))
for i in range(1,number_waves):
    viral_intensity = np.add(viral_intensity,random.choices(range(1,100), k = len(variant_type)))
    variants = np.append(variants,random.choices(variant_type, weights=viral_intensity, k=int(len(N)/number_waves)))

# Select region
weight_region = random.choices(range(1,1000), k = len(regions))
region_index = random.choices(range(0,len(regions)), weights = weight_region, k=int(len(N)/number_waves))
for i in range(1,number_waves):
    weight_region = np.add(weight_region,random.choices(range(1,100), k = len(regions)))
    region_index = np.append(region_index,random.choices(range(0,len(regions)), weights=weight_region, k=int(len(N)/number_waves)))

patient_region = regions.iloc[region_index]

# Union all data
patient = pd.DataFrame({'id':N,'icuAdmitted':icuadmitted,
              'icuDate':date_icu,'deceased':deceased,
              'deathDate':date_dead, 'variant':variants, 
              'Region':patient_region['Region'],
              'State':patient_region['State']}).reset_index(drop = True)

# correct dates
patient.loc[np.where(patient['deceased'] == 0)[0],'deathDate'] = None
patient.loc[np.where(patient['icuAdmitted'] == 0)[0],'icuDate'] = None
patient.loc[np.where(patient['deathDate'] < patient['icuDate'])[0],['icuDate','deathDate']] = patient.iloc[np.where(patient['deathDate'] < patient['icuDate'])[0]][['deathDate','icuDate']].rename(columns = {'deathDate':'icuDate','icuDate':'deathDate'})

patient.to_csv("patients.csv", index_label=None)


