# update sqlite db
# note: missing checks/tests !!!

import codecs
from contextlib import closing
import csv
import requests
import sqlite3
import yaml

path = "/home/michal/project/pollster.eu/dev/datasette/create/"

settings = yaml.safe_load(open(path + "settings.yaml"))

conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
curs = conn.cursor()


def insert(name, keys):
    li = ['?'] * len(keys)
    return "INSERT INTO " + name + "(" + ','.join(keys) + ") VALUES (" + ','.join(li) + ");"


for source in settings['sources']:
    with closing(requests.get(source['url'], stream=True)) as r:
        dr = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        for row in dr:
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
            try:
                curs.execute(insert(source['name'], keys), data)
            except Exception as e:
                # print(e)
                # print(source['name'], data)
                nothing = None

conn.commit()
conn.close()
