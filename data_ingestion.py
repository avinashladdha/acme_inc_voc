import pandas as pd 
import numpy as np


data = pd.read_csv('/Users/avinashladdha/Desktop/df_dash_v1.csv')
## Adding jitter in date of review to better bvisualise the data
min_date = pd.to_datetime('2015-08-01')
max_date = pd.to_datetime('2015-09-05')
d = (max_date - min_date).days + 1

data['review_date'] = min_date + pd.to_timedelta(np.random.randint(d,size=10000), unit='d')


# Write dataframe to data folder 

data.to_csv('./data/df_raw.csv', index = False)
#data.to_csv('/Users/avinashladdha/Desktop/df_dash_rest.csv')




