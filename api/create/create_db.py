# create empty sqlite db

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

# sql to create table
# https://sqlite.org/foreignkeys.html
def create_create(name, arr, fkeys):
    fk = []
    for fkey in fkeys:
        fk.append('FOREIGN KEY(' + fkey['table']['column'] + ') REFERENCES ' + fkey['foreign']['name'] + '(' + fkey['foreign']['column'] + ')')
    fkstring = ','.join(fk)
    if len(fkstring) > 0:
        fkstring = ', ' + fkstring
    return "CREATE TABLE " + name + "(" + ','.join(arr) + fkstring + ");"

# sql to add unique contraints
# http://www.sqlite.org/lang_createtable.html
def create_unique(name, arr):
    return "CREATE UNIQUE INDEX " + name + ''.join(arr) + " ON " + name + "(" + ','.join(arr) + ");"

# prepare foreign keys
fkeys = {}
for k in settings['keys']['foreign']:
    try:
        fkeys[k['table']['name']]
    except Exception:
        fkeys[k['table']['name']] = []
    fkeys[k['table']['name']].append(k)

# create tables with foreign keys
for source in settings['sources']:
    try:
        fkeys[source['name']]
    except Exception:
        fkeys[source['name']] = []
    with closing(requests.get(source['url'], stream=True)) as r:
        csvr = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        for row in csvr:
            break
        for excl in settings['exclude']:
            try:
                row.remove(excl)
            except Exception:
                nothing = None
        r = []
        for k in row:
            r.append(k.replace(':', '_'))
        for k in row:
            arr = k.split(':')
            try:
                foreign = {
                    'name': arr[0] + 's',   # simple pluralization **
                    'column': arr[1]
                }
                table = {
                    'name': source['name'],
                    'column': k.replace(':', '_')
                }
                fkeys.append({
                    'table': table,
                    'foreign': foreign
                })
            except Exception:
                nothing = 0
        query = create_create(source['name'], r, fkeys[source['name']])
        conn.execute(query)


# create unique keys
ukeys = {}
with closing(requests.get(settings['keys']['url'], stream=True)) as r:
    csvr = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
    for row in csvr:
        try:
            ukeys[row['table']]
        except Exception:
            ukeys[row['table']] = []
        ukeys[row['table']].append(row['column'].replace(':', '_'))

for k in ukeys:
    query = create_unique(k, ukeys[k])
    conn.execute(query)

conn.commit()
conn.close()
