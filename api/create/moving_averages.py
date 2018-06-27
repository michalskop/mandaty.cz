# moving averages
import copy
import datetime
import json
import sqlite3
import yaml

path = "/home/michal/project/mandaty.cz/api/create/"

settings = yaml.safe_load(open(path + "settings.yaml"))

conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
curs = conn.cursor()

# prepare data
query = "SELECT * FROM last_term_data"
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()


# select parties
i = 0
name2column = {}
for key in keys:
    name2column[key] = i
    i += 1

selected_parties = []
for row in rows:
    if (row[name2column['value']] > 0.05 or (row[name2column['value']] > 0.01 and row[name2column['topic_id']] == settings['election_topic_id'])) and row[name2column['choice_abbreviation']] not in selected_parties and row[name2column['choice_abbreviation']] is not None:
        selected_parties.append(row[name2column['choice_abbreviation']])

data = []
for row in rows:
    if row[name2column['choice_abbreviation']] in selected_parties:
        item = {}
        for key in keys:
            item[key] = row[name2column[key]]
        data.append(item)


data_obj = {}
for row in data:
    try:
        data_obj[row['choice_abbreviation']]
    except Exception:
        data_obj[row['choice_abbreviation']] = []
    data_obj[row['choice_abbreviation']].append(row)


# calculate moving averages
def fromisoformat(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')


results = []
for k in data_obj:
    items = data_obj[k]
    for i, it in enumerate(items):
        value = 0
        w = 0
        for it2 in items:
            if it2['poll_end_date'] <= it['poll_end_date']:
                delta = fromisoformat(it['poll_end_date']) - fromisoformat(it2['poll_end_date'])
                w += float(it2['pollster_score']) * (1 / 2) ** (delta.days / 30)
                value += (1 / 2) ** (delta.days / 30) * float(it2['value']) * float(it2['pollster_score'])
        # print(i, w)
        res = it
        res['value'] = value / w
        results.append(res)


# insert into db
def insert(name, keys):
    li = ['?'] * len(keys)
    return "INSERT INTO " + name + "(" + ','.join(keys) + ") VALUES (" + ','.join(li) + ");"


for result in results:
    items = []
    for k in keys:
        items.append(result[k])
    try:
        curs.execute(insert('last_term_moving_averages', keys), items)
    except Exception:
        nothing = None
conn.commit()


# prepare file
data = {'election_data': [], 'choices': [], 'moving_averages': [], 'dates': []}

query = 'SELECT * FROM last_term_moving_averages WHERE topic_id = ? ORDER BY value;'
curs.execute(query, [settings['election_topic_id']])
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
i = 0
k2c = {}
for key in keys:
    k2c[key] = i
    i += 1
for row in rows:
    data['election_data'].append({
        'name': row[k2c['choice_abbreviation']],
        'value': row[k2c['value']],
        'color': row[k2c['color_color']]
    })

ordered_parties = []
query = 'SELECT * FROM last_term_moving_averages ORDER BY poll_end_date DESC, value DESC;'
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
i = 0
k2c = {}
for key in keys:
    k2c[key] = i
    i += 1
for row in rows:
    if row[k2c['choice_id']] not in ordered_parties:
        ordered_parties.insert(0, row[k2c['choice_id']])

# query = 'SELECT max(poll_end_date) FROM last_term_moving_averages;'
# curs.execute(query)
# conn.commit()
# rows = curs.fetchall()
# last_date = rows[0][0]
#
# query = 'SELECT pollster_id, poll_identifier FROM last_term_moving_averages WHERE poll_end_date = ?;'
# curs.execute(query, [last_date])
# conn.commit()
# rows = curs.fetchall()
# last_poll = rows[0]

query = 'SELECT * FROM last_term_moving_averages ORDER BY poll_end_date, value'
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
i = 0
k2c = {}
for key in keys:
    k2c[key] = i
    i += 1
polls = {}
dates = []
parties = {}
i = 0
for row in rows:
    try:
        polls[row[k2c['pollster_id']] + row[k2c['poll_identifier']]]
    except Exception:
        polls[row[k2c['pollster_id']] + row[k2c['poll_identifier']]] = i
        i += 1
        dates.append(row[k2c['poll_end_date']])
    try:
        parties[row[k2c['choice_id']]]
    except Exception:
        parties[row[k2c['choice_id']]] = {
            'name': row[k2c['choice_abbreviation']],
            'color': row[k2c['color_color']]
        }
data['dates'] = dates
moving_averages = copy.deepcopy(parties)
for k in parties:
    parties[k]['data'] = [''] * len(polls)
    moving_averages[k]['data'] = [''] * len(polls)

for row in rows:
    i = polls[row[k2c['pollster_id']] + row[k2c['poll_identifier']]]
    moving_averages[row[k2c['choice_id']]]['data'][i] = row[k2c['value']]

query = 'SELECT * FROM last_term_data;'
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
i = 0
k2c = {}
for key in keys:
    k2c[key] = i
    i += 1
for row in rows:
    i = polls[row[k2c['pollster_id']] + row[k2c['poll_identifier']]]
    try:
        parties[row[k2c['choice_id']]]['data'][i] = row[k2c['value']]
    except Exception:
        nothing = None

for op in ordered_parties:
    data['choices'].append(parties[op])
    data['moving_averages'].append(moving_averages[op])

with open(path + settings['app_data_path'] + 'last_term_moving_averages.json', 'w') as fin:
    json.dump(data, fin)

conn.close()
