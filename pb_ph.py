#!/usr/bin/python -B

import datetime
import re
import requests
import sqlite3
import sys

formats = [
    ['1997-11-01', 55, 42],
    ['2009-01-07', 59, 39],
    ['2012-01-18', 59, 35],
    ['2015-10-07', 69, 26]
]


def by_date(item):
    return item[1][0]

def by_freq(item):
    return item[1][1]


site = sys.argv[1]

db = sqlite3.connect('games.db')
c = db.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pb'")
if c.fetchone()[0] == 0:
    db.execute("CREATE TABLE pb (date, b1, b2, b3, b4, b5, b6)")


c = db.execute("SELECT max(date) FROM pb")
last = c.fetchone()[0]
if last is None:
    last = '1997-11-01'
yr0 = int(re.split('-', last)[0])
yr1 = datetime.date.today().year + 1

for year in range(yr0, yr1):
    for half in [('01-01', '06-30'), ('07-01', '12-31')]:
        response = requests.get(
            'https://www.%s.com/api/v1/numbers/%s?_format=json&' % (site, site) +
                'min=%s-%s&' % (year, half[0]) +
                'max=%s-%s' % (year, half[1]),
            verify = False,
            headers = {'Content-Type':'application/json'})

        drawings = response.json()
        for drawing in drawings:
            date = drawing['field_draw_date']
            c = db.execute("SELECT count(date) FROM pb WHERE date='%s'" % date)
            if c.fetchone()[0] == 0:
                b = re.split(',', drawing['field_winning_numbers'])
                db.execute("INSERT INTO pb VALUES ('%s', '%02d', '%02d', '%02d', '%02d', '%02d', '%02d')" %
                           (date, int(b[0]), int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])))
db.commit()


c = db.execute("SELECT * FROM pb ORDER BY date")
nb = {}
pb = {}
mn = 0
mo = 0
mp = 0
for r in c:
    if r[0] == '2009-01-07':
        for n in nb.items():
            mn = n[1][1] if n[1][1] < mn or mn == 0 else mn
    if r[0] == '2012-01-18':
         for n in range(56, 60):
             nb['%02d' % n][1] += mn
 
    if r[0] == '2012-01-18':
        for n in nb.items():
            mo = n[1][1] if n[1][1] < mo or mo == 0 else mo
    if r[0] == '2015-10-07':
        for n in range(60, 60):
            print('no adjustment')
            nb['%02d' % n][1] += mo

    if r[0] == '2015-10-07':
        for n in nb.items():
            mp = n[1][1] if n[1][1] < mp or mp == 0 else mp
    if r[0] == last:
        for n in range(60, 70):
            nb['%02d' % n][1] += mp

    for n in range(1, 6):
        if r[n] not in nb.keys():
            nb[r[n]] = ['', 0]
        nb[r[n]][0] = r[0]
        nb[r[n]][1] += 1
 
    if r[6] not in pb.keys():
        pb[r[6]] = ['', 0]
    pb[r[6]][0] = r[0]
    pb[r[6]][1] += 1
db.close()


for n in sorted(nb.items(), key=by_freq, reverse=True):
    print(n)

print('')

for p in sorted(pb.items(), key=by_date, reverse=True):
    if p[0] < '27':
        print(p)
