# This script runs through the raw csv file, which has a line for each log, 
# and counts to see how many logs there are in each cache.

import numpy as np
import pandas as pd

df = pd.read_csv('./data/caches_raw.csv')

names = list(df['Name'].unique())
num_logs = []
for n,name in enumerate(names):
    num_logs.append(df[df['Name']==name].shape[0])
    if n%50==0: print(f'Name # {n} of {len(names)} completed.')

num_logs = np.array(num_logs)
print(f'There are {len(names)} Caches in this dataset.')
print(f'Number of Logs per cache is between {np.min(num_logs)} and {np.max(num_logs)}, with a mean of {np.mean(num_logs)}.')