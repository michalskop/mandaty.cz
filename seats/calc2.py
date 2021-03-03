"""Estimation of number of seats in CZ parliament based on pollsters' potentials."""
# !!! NOTE: HTML in /home/michal/dev/dark_corners/flow/test4/

import copy
import csv
import datetime
import json
import numpy
import operator

path = "/home/michal/project/mandaty.cz/seats/"

# date = "2019-10-01"
datestring = datetime.datetime.today().strftime('%Y-%m-%d')
inputfile = "mandaty.csv"
# inputfile = "party_sociologu201706_kdustan.csv"
outputfile = "stats.json"
outputrichfile = "current_seats.json"
lastresultsfile = "psp2017_results_selected.csv"
lastregionalfile = "psp2017_selected.csv"
lastseats = "psp2017_seats.csv"
coalitionsinfile = "coalitions.csv"
coalitionsoutfile = "current_coalitions.json"
n = 770
runs = 100


def dhondt(parties, seats):
    """D'Hondt."""
    line = []
    for k in parties:
        for j in range(1, seats + 1):
            line.append({
                'party_code': k,
                'value': parties[k] / j
            })
    line_sorted = sorted(line, key=lambda x: x['value'], reverse=True)
    nof_seats = {}
    for k in parties:
        nof_seats[k] = 0
    for j in range(0, seats):
        nof_seats[line_sorted[j]['party_code']] += 1
    return nof_seats


trial_seats = {}
# current data / polls
current_poll = {}
with open(path + inputfile) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        current_poll[row['party_code']] = row

# gains 2017
gains_prev = {}
with open(path + lastresultsfile) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        gains_prev[row['party_code']] = row

# votes 2017
votes_prev = {}
with open(path + lastregionalfile) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        try:
            votes_prev[row['party_code']]
        except Exception:
            votes_prev[row['party_code']] = {}
        votes_prev[row['party_code']][row['region_code']] = row

# votes 2017 totals
votes_totals_prev = {}
for k in votes_prev:
    s = 0
    for j in votes_prev[k]:
        s += int(votes_prev[k][j]['votes'])
    votes_totals_prev[k] = s

# seats in regions
regions_seats = {}
with open(path + lastseats) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        regions_seats[row['region_code']] = row


def calculate_seats(current):
    """Calculate seats from poll."""
    # calculated no of votes
    calc_nof_votes = {}
    for k in current:
        party_code_prev = current[k]['party_code_2017']
        if float(current[k]['gain']) >= float(current[k]['needs']):
            calc_nof_votes[k] = float(current[k]['gain']) / float(gains_prev[party_code_prev]['gain']) * votes_totals_prev[party_code_prev]
        else:
            calc_nof_votes[k] = 0

    # calculated no of votes by regions
    calc_nof_votes_regions = {}
    for k in calc_nof_votes:
        party_code_prev = current[k]['party_code_2017']
        for j in regions_seats:
            try:
                calc_nof_votes_regions[j]
            except Exception:
                calc_nof_votes_regions[j] = {}
            calc_nof_votes_regions[j][k] = calc_nof_votes[k] / votes_totals_prev[party_code_prev] * int(votes_prev[party_code_prev][j]['votes'])

    # calculate total seats
    calc_seats = {}
    for k in current:
        calc_seats[k] = 0

    for j in regions_seats:
        calculated = dhondt(calc_nof_votes_regions[j], int(regions_seats[j]['seats']))
        # if j == 'pa':
        #     print(j, calculated['pirati'])
        for k in current:
            calc_seats[k] += calculated[k]

    return calc_seats


for i in range(0, runs):
    # randomize sample
    current = copy.deepcopy(current_poll)
    for k in current_poll:
        current[k]['gain'] = numpy.random.binomial(n, float(current[k]['gain'])) / n

    calc_seats = calculate_seats(current)

    for k in calc_seats:
        try:
            trial_seats[k]
        except Exception:
            trial_seats[k] = []
        trial_seats[k].append(calc_seats[k])

seats = calculate_seats(current_poll)

stats = []
for k in trial_seats:
    try:
        difference = seats[k] - int(gains_prev[current_poll[k]['party_code_2017']]['seats'])
        # difference = seats[k] - int(current_poll[k]['seats_2017'])
    except Exception:
        difference = seats[k]
    row = {
        'party_code': k,
        'median': sorted(trial_seats[k])[round(runs * 0.5)],
        'lo': sorted(trial_seats[k])[round(runs * 0.05)],
        'hi': sorted(trial_seats[k])[round(runs * 0.95)],
        'seats': seats[k],
        'difference': difference,
        'name': current_poll[k]['name'],
        'color': current_poll[k]['color'],
        'gain': current_poll[k]['gain']
    }
    print(row)
    stats.append(row)

stats.sort(key=operator.itemgetter("gain"), reverse=True)
stats.sort(key=operator.itemgetter("hi"), reverse=True)
stats.sort(key=lambda x: x['seats'], reverse=True)
with open(path + outputfile, "w") as fout:
    json.dump(stats[0:9], fout)

with open(path + outputrichfile, "w") as fout:
    rich = {
        "data": stats[0:9],
        "date": datestring
    }
    json.dump(rich, fout, ensure_ascii=False)


def majority_probability(seats, majority=101):
    """Probability of majority."""
    over = 0
    for i in range(0, runs):
        s = 0
        for k in seats:
            s += seats[k][i]
        if s >= majority:
            over += 1
    return over / runs


def coalition_seats(trial_seats, party_codes):
    """Calculate the number of seats for a coalition."""
    ss = []
    for run in range(0, runs):
        sm = 0
        for code in party_codes:
            sm += trial_seats[code][run]
        ss.append(sm)
    return ss


# coalitions
coalitions = []
potentials = []
# single party
for k in trial_seats:
    potentials.append({
        'trial_seats': {k: trial_seats[k]},
        'seats': seats[k],
        'party_code': k,
        'keys': [k]
    })
# two parties
for k in trial_seats:
    for m in trial_seats:
        if k < m:
            potentials.append({
                'trial_seats': {k: trial_seats[k], m: trial_seats[m]},
                'seats': sorted(coalition_seats(trial_seats, [k, m]))[round(runs * 0.5)],
                'party_code': '+'.join([k, m]),
                'keys': [k, m]
            })
# multiple parties
with open(path + coalitionsinfile) as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        keys = row['party_code'].split('+')
        ts = {}
        for key in keys:
            ts[key] = trial_seats[key]
        potentials.append({
            'trial_seats': ts,
            'seats': sorted(coalition_seats(trial_seats, keys))[round(runs * 0.5)],
            'party_code': row['party_code'],
            'keys': keys
        })

# colors and names
code2data = {}
for s in stats:
    code2data[s['party_code']] = {
        'name': s['name'],
        'color': s['color']
    }

# try potentials
for p in potentials:
    mp = majority_probability(p['trial_seats'])
    if mp > 0:
        item = {
            'party_code': p['party_code'],
            'seats': p['seats'],
            'majority_probability': mp,
            'party_codes': p['keys']
        }
        coalitions.append(item)
coalitions.sort(key=lambda x: x['majority_probability'], reverse=True)

with open(path + coalitionsoutfile, "w") as fout:
    it = {
        "coalitions": coalitions,
        "meta": code2data,
        "date": datestring
    }
    json.dump(it, fout)

# seats for a party:
# with open(path + code + "_pirateseats.csv", "w") as fout:
#     dw = csv.DictWriter(fout, ['seats'])
#     dw.writeheader()
#     for row in trial_seats['pirati']:
#         dw.writerow({'seats': row})
