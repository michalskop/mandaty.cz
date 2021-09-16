"""Simulations using multivariate normal distribution."""

import warnings
warnings.filterwarnings("ignore")

import csv
import datetime
import json
import math
import numpy as np
import pandas as pd
import scipy.stats

path = "/home/michal/project/mandaty.cz/seats/"

datestring = datetime.datetime.today().strftime('%Y-%m-%d')

inputfile = "mandaty.csv"
inputfile = "mandaty_test.csv"

# outputfile = "stats_multi.json"
# outputrichfile = "current_seats_multi.json"
lastresultsfile = "psp2017_results_selected.csv"
lastregionalfile = "psp2017_selected.csv"
lastseats = "psp2017_seats.csv"
coalitionsinfile = "coalitions.csv"
coalitionsoutfile = "current_coalitions.json"
n = 770
runs = 1000

# current data / poll
current_poll = pd.read_csv(path + inputfile)
current_poll = current_poll.set_index('party_code', drop=False)
current_poll['value'] = current_poll['gain']

# last results
last_results = pd.read_csv(path + lastresultsfile)

# parties
ps = current_poll['party_code'].tolist()
parties = pd.DataFrame(columns=ps)

# last regional results
last_regional_results = pd.read_csv(path + lastregionalfile)

total_last_votes = pd.pivot_table(data=last_regional_results, values='votes', index='region_code', aggfunc=scipy.sum).reset_index().sum()['votes']

# correlation matrix
lrr_denormalized = pd.pivot_table(last_regional_results, index='region_code', columns='party_code', values='votes')
lrrd_perc = lrr_denormalized.div(lrr_denormalized.sum(axis=1), axis=0)
correlation = lrrd_perc.corr()

# seats in regions
regions_seats = pd.read_csv(path + lastseats)

# last votes
last_votes = pd.pivot_table(data=last_regional_results, values='votes', index='party_code', aggfunc=scipy.sum).reset_index()

# regions
region_codes = regions_seats['region_code'].tolist()

# covariance matrix
n = 777
coef = 2
sd = (n * current_poll['gain'] * (1 * current_poll['gain'])).apply(math.sqrt) / n * coef
np.inner(np.inner(sd.transpose(), correlation), sd.transpose())
