import pandas as pd
import numpy as np
import re, os
from collections import OrderedDict

from clean import target_columns, data_columns
from utils import log_dropped_data, find_most_recent_file, cache_df, to_drop, target_columns


target_columns = [tc for tc in target_columns if tc not in ['TOTAL_DELAY', 'DELAYED']]

def set_delayed_threshold(df, minutes=30):
	df['TOTAL_DELAY'] = df[target_columns].sum(axis=1)
	df['DELAYED'] = df['TOTAL_DELAY'] > minutes
	target_columns.extend(['TOTAL_DELAY', 'DELAYED'])
	return df

# column : number of bins
to_bin = {
    'DAY_OF_MONTH':4,
    'CRS_DEP_TIME':24,
    'CRS_ELAPSED_TIME':12,
    'DAY_OF_MONTH':10,
}

def bin_column(df, column, num_bins):
    return np.round(df[column]/num_bins)

def bin_transform(df):
	print 'bin transforming some columns'
	for column, num_bins in to_bin.iteritems():
		df[column] = bin_column(df, column, num_bins)
	return df

to_dummy = OrderedDict([
    ('UNIQUE_CARRIER',0.8),
	('ORIGIN_AIRPORT_ID',0.8),
    ('DEST_AIRPORT_ID',0.8),
    # ('FL_NUM',0.5),
    # ('TAIL_NUM',0.95),
    ('QUARTER','all'),
    
])

def dummy_transform(df):
	print 'print getting dummy variables'
	to_dummy.update(to_bin)
	for column, vc in to_dummy.iteritems():
		if isinstance(vc, int) or vc=='all':
			to_keep = df[column].unique()
		else:
			df_vc = df[column].value_counts()
			to_keep = df_vc[df_vc.cumsum() < vc*len(df)].index
		old_len = len(df)
		df = df[df[column].isin(to_keep)]
		log_dropped_data(old_len, df, 'keeping {0} dummy columns for {1}'.format(len(to_keep), column))
	print 'final df length: {}'.format(len(df))
	print 'getting dummies'
	df = pd.get_dummies(df, columns=to_dummy)
	return df

def engineer_features():
	infile = find_most_recent_file('clean')
	df = pd.read_pickle(infile)
	df = set_delayed_threshold(df)
	df = bin_transform(df)
	df = dummy_transform(df)
	return df, infile

def main():
	df, infile = engineer_features()
	cache_df(df, 'fe', infile)

if '__main__' in __name__:
	main()
