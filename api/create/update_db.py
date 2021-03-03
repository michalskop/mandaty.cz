# update sqlite db
# note: missing checks/tests !!!

import codecs
from contextlib import closing
import csv
import requests
import sqlite3
import yaml

path = "/home/michal/project/mandaty.cz/api/create/"

settings = yaml.safe_load(open(path + "settings.yaml"))

conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
curs = conn.cursor()


def _insert(name, keys):
    nkeys = []
    for key in keys:
        if key.strip() != '':
            nkeys.append(key)
    if name == 'polls':
        print(nkeys)
    li = ['?'] * len(nkeys)
    return "INSERT INTO " + name + "(" + ','.join(nkeys) + ") VALUES (" + ','.join(li) + ");"


for source in settings['sources']:
    with closing(requests.get(source['url'], stream=True)) as r:
        dr = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        for row in dr:
            if source['name'] == 'polls':
                print(row)
                xrow = row
                xsource = source
            data = []
            keys = []
            for k in row:
                if k not in settings['exclude']:
                    if k == 'value':
                        data.append(float(row[k].replace('%', '')) / 100)
                    else:
                        data.append(row[k])
                    if ':' in k:
                        keys.append(k.replace(':', '_'))
                    else:
                        keys.append(k)
                if source['name'] == 'polls':
                    xkeys = keys
                    xdata = data
            try:
                curs.execute(_insert(source['name'], keys), data)
            except Exception as e:
                # if source['name'] == 'polls': 
                #     print(e)
                #     print(source['name'], data)
                #     break
                nothing = None

conn.commit()
conn.close()

# query ="UPDATE polls SET end_date='2018-05-24' WHERE end_date='2018-05'"

# query = "UPDATE last_term_data SET color='#000000' WHERE 

# conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
# curs = conn.cursor()
# query = "SELECT * FROM last_term_data WHERE poll_identifier='2021-01'"
# query = "UPDATE choices SET abbreviation='SPOLU' WHERE id='SPOLU';"
# curs.execute(query)
# #d = curs.fetchall()
# conn.commit()
# conn.close()
