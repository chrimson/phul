#!/usr/bin/python -B

import datetime as dt
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


site = None
if len(sys.argv) == 2:
    site = sys.argv[1]

db = sqlite3.connect('games.db')

c = db.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pb'")
if site is not None and c.fetchone()[0] == 0:
    db.execute("CREATE TABLE pb (date, b1, b2, b3, b4, b5, b6)")

c = db.execute("SELECT max(date) FROM pb")
lt = c.fetchone()[0]
if lt is None:
    lt = formats[0][0]
last = dt.date(int(lt[0:4]), int(lt[5:7]), int(lt[8:10]))
today = dt.date.today()

yr0 = last.year
yr1 = today.year

if site is not None and (today - last).days > 2:
    for year in range(yr0, yr1 + 1):
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


c = db.execute("SELECT max(date) FROM pb")
lt = c.fetchone()[0]
formats.append([lt])

c = db.execute("SELECT * FROM pb ORDER BY date")
nb = {}
pb = {}
mn = []
for m in range(len(formats) - 1):
    mn.append(0)

for r in c:
    for f in range(1, len(formats) - 1):
        if r[0] == formats[f][0]:
            for n in nb.items():
                mn[f] = n[1][1] if n[1][1] < mn[f] or mn[f] == 0 else mn[f]

        if r[0] == formats[f + 1][0]:
            for n in range(formats[f - 1][1] + 1, formats[f][1] + 1):
                nb['%02d' % n][1] += mn[f]
 
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


for n in sorted(nb.items(), key=by_date, reverse=True):
    print(n)
print()

for n in sorted(nb.items(), key=by_freq, reverse=True):
    print(n)
print()

for p in sorted(pb.items(), key=by_date, reverse=True):
    if p[0] < '27':
        print(p)
print()

for p in sorted(pb.items(), key=by_freq, reverse=True):
    if p[0] < '27':
        print(p)
print()
