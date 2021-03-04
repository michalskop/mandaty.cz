"""Estimation of number of seats in CZ parliament based on models, version 2021."""

import copy
import csv
import datetime
import json
import math
import numpy as np
import pandas as pd
import scipy.stats
import operator

path = "/home/michal/project/mandaty.cz/seats/"

datestring = datetime.datetime.today().strftime('%Y-%m-%d')

inputfile = "mandaty.csv"
outputfile = "stats.json"
outputrichfile = "current_seats.json"
lastresultsfile = "psp2017_results_selected.csv"
coalitionsinfile = "coalitions.csv"
coalitionsoutfile = "current_coalitions.json"
n = 770
runs = 10000

""" D'Hondt """
def dhondt(parties, seats):
    """D'Hondt."""
    line = []
    for party in parties:
        for j in range(1, seats + 1):
            line.append({
                'party_code': party['party_code'],
                'value':  party['value'] / j
            })
    line_sorted = sorted(line, key=lambda x: x['value'], reverse=True)
    nof_seats = {}
    for party in parties:
        k = party['party_code']
        nof_seats[k] = 0
    for j in range(0, seats):
        nof_seats[line_sorted[j]['party_code']] += 1
    return nof_seats
 

def randomized_sample(cp, n, coef = 2):
    cp['sdx'] = (n * cp['gain'] * (1 - cp['gain'])).apply(math.sqrt) / n * coef
    cp['rand'] = scipy.stats.norm.rvs(loc=cp['gain'], scale=cp['sdx'])
    ins = cp[cp['rand'] > cp['needs']]
    s = sum(ins['rand'])
    ins['value'] = ins['rand'] / s
    d = []
    for row in ins.iterrows():
        d.append({
                'party_code': row[1]['party_code'],
                'value': row[1]['value']
            })
    return d 

# current data / poll
current_poll = pd.read_csv(path + inputfile)
current_poll = current_poll.set_index('party_code', drop=False)

# last results
last_results = pd.read_csv(path + lastresultsfile)

# parties
ps = current_poll['party_code'].tolist()
parties = pd.DataFrame(columns=ps)

# best estimate
d = []
ins = current_poll[current_poll['gain'] > current_poll['needs']]
for row in ins.iterrows():
    d.append({
        'party_code': row[1]['party_code'],
        'value': row[1]['gain']
    })
seats = pd.DataFrame(columns=ps)
seats = seats.append(dhondt(d, 200), ignore_index=True)

# randomized samples
for i in range(0, runs):
    sample = randomized_sample(current_poll, n)
    calc_seats = dhondt(sample, 200)
    parties = parties.append(calc_seats, ignore_index=True)

parties = parties.fillna(0)

# stats
stats = pd.DataFrame(index=ps)
stats['party_code'] = ps
stats['median'] = parties.median(0)
stats['lo'] = parties.quantile(q=0.05, interpolation='nearest')
stats['hi'] = parties.quantile(q=0.95, interpolation='nearest')
stats['difference'] = seats.transpose().fillna(0).rename(columns={0: 'seats'})['seats'].to_frame() - (stats.merge(last_results.loc[:, ['party_code', 'seats']], how='left', left_on='party_code', 
right_on='party_code')).fillna(0)['seats'].to_frame().set_index(pd.Index(ps))
stats['seats'] = seats.transpose().fillna(0)
stats['name'] = current_poll['name']
stats['color'] = current_poll['color']
stats['gain'] = current_poll['gain']

stats = stats.sort_values(['seats', 'hi', 'gain'], ascending=[False, False, False])

stats.to_json(path + outputfile, force_ascii=False, orient='records')

with open(path + outputrichfile, "w") as fout:
    rich = {
        "data": stats[stats['hi'] > 0].to_dict(orient='records'),
        "date": datestring
    }
    json.dump(rich, fout, ensure_ascii=False)


# coalitions
coalitions = []
majority = 101

def _coalition_probability(parties, party_codes, runs, majority):
    t = parties.loc[:,party_codes]
    # note: all members of coalition has to have >0 seats
    return ((t.sum(axis=1) >= majority) * np.sign((parties.loc[:, party_codes]).product(axis=1))).sum() / runs

# single parties
for row in stats.iterrows():
    it = {
        'party_code': row[1]['party_code'],
        'seats': row[1]['seats'],
        'majority_probability': _coalition_probability(parties, [row[1]['party_code']], runs, majority),
        'party_codes': [row[1]['party_code']]
    }
    if it['majority_probability'] > 0:
         coalitions.append(it)

# two parties
for p in ps:
    for q in ps:
        if p < q:
            it = {
                'party_code': '*'.join([p, q]),
                'seats': stats.loc[p]['seats'] + stats.loc[q]['seats'],
                'majority_probability': _coalition_probability(parties, [p, q], runs, majority),
                'party_codes': [p, q]
            }
            if it['majority_probability'] > 0:
                coalitions.append(it)

# multiple parties
with open(path + coalitionsinfile) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        keys = row['party_code'].split('*')
        it = {
            'party_code': '*'.join(keys),
            'seats': stats.loc[keys]['seats'].sum(),
            'majority_probability': _coalition_probability(parties, keys, runs, majority),
            'party_codes': keys
        }
        if it['majority_probability'] > 0:
            coalitions.append(it)

coalitions.sort(key=lambda x: x['majority_probability'], reverse=True)



with open(path + coalitionsoutfile, "w") as fout:
    it = {
        "coalitions": coalitions,
        "meta": current_poll.loc[:, ['name', 'color']].to_dict('index'),
        "date": datestring
    }
    json.dump(it, fout)
