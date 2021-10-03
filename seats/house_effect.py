"""House effect from GSheet."""
# Python >= 3.7
# Pandas >= 1.2

import datetime
# import functools
import gspread
# import locale
import numpy as np
import pandas as pd

gc = gspread.service_account()

# Pollster CZ
# parameters
sheetkey = "1a9zd3ThneSR7JN7-wj4uw5hBBggY9NyguFYIb4jbAc0"
# sheetkey = "1UBu8pM1Yfwm1ovyzK_52p1CFiLzGoTJRzooCfJEID-A"
# since = '2017-11-01'
since = '2021-01-01'
exclude_limit = 0.02
# exclude_pollsters = ['STEM/MARK', 'Phoenix Research', 'Sanep']
exclude_pollsters = ['STEM/MARK', 'Ipsos']
excludes = ['odmítli', 'jiné strany']

today = datetime.date.today()

# load data from GSheet
sh = gc.open_by_key(sheetkey)

ws = sh.worksheet('polls')
dfpolls = pd.DataFrame(ws.get_all_records())

ws = sh.worksheet('data')
dfdata = pd.DataFrame(ws.get_all_records())
# convert percentage string to float
dfdata['value'] = dfdata['value'].apply(lambda x: float(x.strip('%'))/100)

# filter polls
polls = dfpolls[(dfpolls['start_date'] >= since) & ~(dfpolls['pollster:id'].isin(exclude_pollsters))]
data_all = polls.merge(dfdata, how='left', left_on=['identifier', 'pollster:id'], right_on=['poll:identifier', 'pollster:id'])
data = data_all[data_all['question:identifier'] == 'model']
# add middle point
data['start_date_date'] = data['start_date'].apply(datetime.date.fromisoformat)
data['end_date_date'] = data['end_date'].apply(datetime.date.fromisoformat)
data['middle_date_date'] = data['start_date_date'] + (data['end_date_date'] - data['start_date_date']) / 2
data['middle_date'] = data['middle_date_date'].apply(datetime.date.isoformat)

# get parties with at least exclude_limit (2.5%) in one poll
pt = pd.pivot_table(data, values='value', index='choice:id', aggfunc=np.max)
pt = pt.reset_index()

parties = pt[(~pt['choice:id'].isin(excludes)) & (pt['value'] > exclude_limit)]['choice:id'].tolist()

# filter data by parties
data_filtered = data[data['choice:id'].isin(parties)]

# calculate poll weights
dfpolls_filtered = dfpolls[(dfpolls['middle_date'].astype(str) > since) & ~(dfpolls['pollster:id'].isin(exclude_pollsters))]
dfpolls_filtered['middle_date_date'] = dfpolls_filtered['middle_date'].apply(datetime.date.fromisoformat)

pw = 1 / dfpolls_filtered.groupby('pollster:id')['identifier'].count()
dfpolls_filtered = dfpolls_filtered.merge(pw, how='left', left_on='pollster:id', right_on='pollster:id').rename(columns={'identifier_y': 'pollster_weight', 'identifier_x': 'identifier'})

dfpolls_filtered['weight'] = (1 / 2) ** (abs(today - dfpolls_filtered['middle_date_date']).apply(datetime.timedelta.total_seconds) / 60 / 60 / 24 / 30) * dfpolls_filtered['pollster_weight']

dfpolls_filtered.groupby('pollster:id').count()
pd.pivot_table(dfpolls_filtered, index='pollster:id', values='weight')

# calculate moving averages
moving_averages = pd.DataFrame(columns=['middle_date', 'middle_date_date', 'choice:id', 'value'])

for party in parties:
    t = data_filtered[data_filtered['choice:id'] == party]
    for md in np.sort(t['middle_date_date'].unique()):
        w = (1 / 2) ** (abs(t['middle_date_date'] - md).apply(datetime.timedelta.total_seconds) / 60 / 60 / 24 / 30)
        v = (t['value'] * w).sum() / w.sum()
        moving_averages = moving_averages.append({
            'middle_date': md.isoformat(),
            'middle_date_date': md,
            'choice:id': party,
            'value': v
        }, ignore_index=True)

# house effect
data_averages = data_filtered.merge(moving_averages, how='left', on=['middle_date', 'choice:id']).drop_duplicates()

data_averages.to_csv('data_averages.csv')

pollsters = polls.pivot_table(values=['identifier'], index=['pollster:id'], aggfunc=np.count_nonzero).reset_index()

house_effect = pd.DataFrame(columns = ['pollster:id', 'choice:id', 'mean', 'sd', 'n'])
for party in parties:
    for index, row in pollsters.iterrows():
        pollster = row['pollster:id']
        t = data_averages[(data_averages['pollster:id'] == pollster) & (data_averages['choice:id'] == party)]
        mean = np.mean((t['value_x'] - t['value_y']))
        sd = np.std((t['value_x'] - t['value_y']), ddof=1)
        house_effect = house_effect.append({
            'choice:id': party,
            'pollster:id': pollster,
            'mean': mean,
            'sd': sd,
            'n': len(t)
        }, ignore_index=True)

house_effect[house_effect['n'] >= 3].pivot_table(values=['mean', 'sd'], index='choice:id', columns='pollster:id').reset_index().to_csv("house_effect.csv")
