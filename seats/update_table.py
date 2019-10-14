"""Update mandaty.csv with new calculated data."""

import csv
import json

path = "/home/michal/project/mandaty.cz/"

with open(path + "frontend/static/data/last_term_moving_averages.json") as fin:
    mas = json.load(fin)

with open(path + "seats/mandaty.csv") as fin:
    dr = csv.DictReader(fin)
    mandates = {}
    for row in dr:
        mandates[row['name']] = row
    header = row.keys()

with open(path + "seats/mandaty.csv", "w") as fout:
    dw = csv.DictWriter(fout, header)
    dw.writeheader()
    for r in mas['moving_averages']:
        party = r['name']
        row = mandates[party]
        if r['data'][-1] != '':
            row['gain'] = r['data'][-1]
        dw.writerow(row)
