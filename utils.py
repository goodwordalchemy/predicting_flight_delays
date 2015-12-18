import pandas as pd
import numpy as np
import re, os
import matplotlib.pyplot as plt

target_columns = [
	'CARRIER_DELAY',
	'WEATHER_DELAY',
	'NAS_DELAY',
	'SECURITY_DELAY',
	'LATE_AIRCRAFT_DELAY',
	'DELAYED',
	'TOTAL_DELAY',
]

to_drop = [
    'YEAR',
    'FL_DATE',
    'FL_NUM',
    'TAIL_NUM',
]

def log_dropped_data(old_len, df, reason):
	new_len = len(df)
	print 'dropped {0}/{1} ({2}%) flights: {3}'.format(
		old_len - new_len,
		old_len,
		round(float(old_len - new_len)/old_len,2),
		reason
	)

def find_most_recent_file(pattern):
	pattern='{}_flights_data(.*?)\.pkl'.format(pattern)
	pattern = re.compile(pattern)
	cache_name = os.path.join('cache')
	cache_files = os.listdir(cache_name)
	match_files = filter(lambda filename: pattern.search(filename), cache_files)
	return os.path.join(cache_name,max(match_files))	

def cache_df(df, prefix, infile):
	outfile = infile.split('/')[-1]
	outfile = outfile.split('_')
	outfile[0] = prefix
	outfile = "_".join(outfile)
	outfile = os.path.join('cache', outfile)
	print 'saving cleaned df to {}'.format(outfile)
	df.to_pickle(outfile)

def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and traning learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : integer, cross-validation generator, optional
        If an integer is passed, it is the number of folds (defaults to 3).
        Specific cross-validation objects can be passed, see
        sklearn.cross_validation module for the list of possible objects

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt