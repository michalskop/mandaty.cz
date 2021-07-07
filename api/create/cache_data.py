# prepare json files for web

import json
import sqlite3
import yaml

path = "/home/michal/project/mandaty.cz/api/create/"

settings = yaml.safe_load(open(path + "settings.yaml"))

conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
curs = conn.cursor()

# last term data
data = {'rows': []}
query = "SELECT * FROM last_term_data WHERE CAST(pollster_score as FLOAT) > 0"
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
for row in rows:
    i = 0
    item = {}
    for key in keys:
        item[key] = row[i]
        i += 1
    data['rows'].append(item)

with open(path + settings['app_data_path'] + "last_term_data.json", "w") as fout:
    json.dump(data, fout)
with open(path + settings['app_data_path_2'] + "last_term_data.json", "w") as fout:
    json.dump(data, fout)

# last term polls
data = {'rows': []}
query = "SELECT * FROM last_term_polls WHERE CAST(pollster_score as FLOAT) > 0"
curs.execute(query)
conn.commit()
keys = list(map(lambda x: x[0], curs.description))
rows = curs.fetchall()
for row in rows:
    i = 0
    item = {}
    for key in keys:
        item[key] = row[i]
        i += 1
    data['rows'].append(item)

with open(path + settings['app_data_path'] + "last_term_polls.json", "w") as fout:
    json.dump(data, fout)
with open(path + settings['app_data_path_2'] + "last_term_polls.json", "w") as fout:
    json.dump(data, fout)
