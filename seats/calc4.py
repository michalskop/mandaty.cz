"""Estimation of number of seats in CZ parliament based on pollsters' potentials."""
# !!! NOTE: HTML in /home/michal/dev/dark_corners/flow/test4/

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
# inputfile = "mandaty_test.csv"
# inputfile = "vysledky_voleb_2017.csv"
outputfile = "stats.json"
outputrichfile = "current_seats.json"
lastresultsfile = "psp2017_results_selected.csv"
lastregionalfile = "psp2017_selected.csv"
lastseats = "psp2017_seats.csv"
coalitionsinfile = "coalitions.csv"
coalitionsoutfile = "current_coalitions.json"
n = 770
runs = 1000

# Imperiali
def imperiali(sample):
    """ Imperiali. """
    regional_sample = last_regional_results.merge(sample, how="left", left_on="party_code", right_on="party_code")
    regional_sample['estimated_votes'] = regional_sample['votes'] * regional_sample['rate']

    regional_seats = pd.DataFrame(columns=['party_code', 'region_code', 'nof_seats', 'rest'])
    for rc in region_codes:
        # 1st scrutinium
        region = regional_sample[regional_sample['region_code'] == rc].reset_index()

        s = region.sum()['estimated_votes']
        rs = (regions_seats[regions_seats['region_code'] == rc]['seats']).iloc[0] # §48 (2)
        N = round(s / (rs + 2)) # krajske volebni cislo §50 (2)

        overs = region[region['value'] > region['needs']]
        overs.loc[:, ('nof_seats')] = (overs.loc[:, ('estimated_votes')].divide(N)).apply(math.floor) # počty mandátů §50 (3)
        overs.loc[:, ('rest')] = overs['estimated_votes'] - overs['nof_seats'] * N  # zbytky §50 (4)
        overs.loc[:, ('rest_rank')] = overs['rest'].rank()# pořadí zbytků §50 (4)

        # correction §50 (4)
        overseats = overs['nof_seats'].sum() - rs
        if overseats > 0:
            print(rc, overseats)
            ioverseats = overs.index[overs['rest_rank'] <= overseats]
            for i in ioverseats:
                overs['nof_seats'][i] -= 1
                overs['rest'][i] = overs['estimated_votes'][i] - overs['nof_seats'][i] * N


        regional_seats = regional_seats.append(overs.loc[:, ['party_code', 'region_code', 'nof_seats', 'rest']], ignore_index=True)

    # 2nd scrutinium
    ss = 200 - regional_seats['nof_seats'].sum()
    rests = regional_seats['rest'].sum()

    RN = rests / (ss + 1)

    extras = pd.pivot_table(regional_seats, values=['rest'], index='party_code', aggfunc=np.sum).reset_index()
    extras.loc[:, ('nof_seats')] = (extras['rest'] / RN).apply(math.floor)
    extras.loc[:, ('rest_rest')] = extras['rest'] - extras['nof_seats'] * RN
    extras.loc[:, ('rank')] = extras['rest_rest'].rank()
    last_rest = ss - extras['nof_seats'].sum()
    extras.loc[:, ('extra')] = extras['nof_seats'] + 1 * (extras['rank'] <= last_rest)

    nof_seats = pd.pivot_table(regional_seats, values=['nof_seats'], index='party_code', aggfunc=np.sum).reset_index()
    nof_seats = nof_seats.merge(extras, how='left', left_on='party_code', right_on='party_code')
    nof_seats.loc[:, ('seats')] = nof_seats['nof_seats_x'] + nof_seats['extra']

    nof_seats = region.loc[:, ['party_code']].merge(nof_seats, how='left', left_on='party_code',right_on='party_code')

    out = nof_seats.loc[:, ('party_code', 'seats')].set_index('party_code').transpose()

    return out


def randomized_sample(cp, n, coef = 2):
    cp['sdx'] = (n * cp['gain'] * (1 - cp['gain'])).apply(math.sqrt) / n * coef
    cp['rand'] = scipy.stats.norm.rvs(loc=cp['gain'], scale=cp['sdx'])
    s = sum(cp['rand'])
    cp['value'] = cp['rand'] / s
    d = []
    for row in cp.iterrows():
        d.append({
                'party_code': row[1]['party_code'],
                'value': row[1]['value'],
                'needs': row[1]['needs']
            })
    return d 


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

# seats in regions
regions_seats = pd.read_csv(path + lastseats)

# last votes
last_votes = pd.pivot_table(data=last_regional_results, values='votes', index='party_code', aggfunc=scipy.sum).reset_index()

# regions
region_codes = regions_seats['region_code'].tolist()


# best estimate
sample = current_poll.reset_index(drop=True).loc[:, ('party_code', 'value', 'needs')]
sample['votes'] = (sample['value'] * total_last_votes).apply(round)
sample = sample.merge(last_votes, how="left", left_on="party_code", right_on="party_code")
sample['rate'] = sample['votes_x'] / sample['votes_y']

seats = imperiali(sample)
seats = seats.fillna(0)

# randomized samples
for i in range(0, runs):
    sample = pd.DataFrame(randomized_sample(current_poll, n))
    sample['votes'] = (sample['value'] * total_last_votes).apply(round)
    sample = sample.merge(last_votes, how="left", left_on="party_code", right_on="party_code")
    sample['rate'] = sample['votes_x'] / sample['votes_y']
    calc_seats = imperiali(sample)
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
stats['in'] = (parties > 0).sum() / runs

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