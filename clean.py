import pandas as pd
import numpy as np
import re, os
import matplotlib.pyplot as plt
from sklearn.learning_curve import learning_curve
from utils import find_most_recent_file, cache_df, log_dropped_data

target_columns = [
	'CARRIER_DELAY',
	'WEATHER_DELAY',
	'NAS_DELAY',
	'SECURITY_DELAY',
	'LATE_AIRCRAFT_DELAY',
]

data_columns = [
	'YEAR',
	'QUARTER',
	'MONTH',
	'DAY_OF_MONTH',
	'FL_DATE',
	'UNIQUE_CARRIER',
	'TAIL_NUM',
	'FL_NUM',
	'ORIGIN_AIRPORT_ID',
	'DEST_AIRPORT_ID',
	'CRS_DEP_TIME',
	'CRS_ELAPSED_TIME',
	'DISTANCE_GROUP',
	'CARRIER_DELAY',
	'WEATHER_DELAY',
	'NAS_DELAY',
	'SECURITY_DELAY',
	'LATE_AIRCRAFT_DELAY',
]

def fill_data(df):
	print 'filling in missing values'
	df[target_columns] = df[target_columns].fillna(0)
	return df

def drop_data(df):
	print 'dropping data...'
	df.drop('Unnamed: 25', inplace=True)
	for reason in ['CANCELLED', 'DIVERTED']:
		old_len = len(df)
		df = df[df[reason]==0]
		log_dropped_data(old_len, df, reason)
	
	df = df[data_columns]
	print 'missing values:'
	print df.isnull().sum()
	
	return df

def clean_data(infile=None, size=5e6):
	print 'loading data from pickle...'
	if infile is None:
		infile = find_most_recent_file('raw')
	df =  pd.read_pickle(infile)
	
	if len(df) > size:
		df = df.sample(size)
	
	df = fill_data(df)
	df = drop_data(df)
	
	return df, infile

def main():
	df, infile = clean_data()
	cache_df(df, 'clean', infile)

if '__main__' in __name__:
	main()