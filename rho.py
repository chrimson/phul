#!/usr/bin/python -B

# Random Hexadraw Orderer

import datetime as dt
import json
import random
import re
import requests
import sqlite3
import sys
import urllib3

formats = [
    ['1997-11-01', 55, 42],
    ['2009-01-07', 59, 39],
    ['2012-01-18', 59, 35],
    ['2015-10-07', 69, 26]
]

def to_date(ds):
    return dt.date(int(ds[0:4]), int(ds[5:7]), int(ds[8:10]))

def by_date(item):
    return item[1][0]

def by_freq(item):
    return item[1][1]


try:
    json.load(open('rho.json', 'r'))
except:
    print('No configuration found')
    exit()

if len(sys.argv) != 2:
    print('Need sequence name')
    exit()
name = sys.argv[1]

db = sqlite3.connect('rho.db')
c = db.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='%s'" % name)
if c.fetchone()[0] == 0:
    db.execute("CREATE TABLE %s (date, b1, b2, b3, b4, b5, b6)" % name)

if name.startswith('sim_'):
    days = 4
    for f in range(len(formats)):

        date = to_date(formats[f][0])
        if f + 1 < len(formats):
            next_fmt = to_date(formats[f + 1][0])
        else:
            next_fmt = dt.date.today() + dt.timedelta(1)

        while date < next_fmt:
            sb = []
            for n in range(0, 5):
                sb.append('"%02d"' % random.randint(1, formats[f][1]))
            sb.append('"%02d"' % random.randint(1, formats[f][2]))
            bs = ','.join(sb)

            c = db.execute('SELECT count(date) FROM %s WHERE date="%s"' % (name, date))
            if c.fetchone()[0] == 0:
                db.execute('INSERT INTO %s VALUES ("%s", %s)' % (name, date, bs))

            date += dt.timedelta(days)
            days = 4 if days == 3 else 3

else:
    c = db.execute("SELECT max(date) FROM %s" % name)
    lt = c.fetchone()[0]
    if lt is None:
        lt = formats[0][0]
    last = to_date(lt)
    today = dt.date.today()
    yr0 = last.year
    yr1 = today.year

    if (today - last).days > 2:
        urllib3.disable_warnings()
        for year in range(yr0, yr1 + 1):
            for half in [('01-01', '06-30'), ('07-01', '12-31')]:
                response = requests.get(
                    'https://www.%s.com/api/v1/numbers/%s?_format=json&' % (name, name) +
                        'min=%s-%s&' % (year, half[0]) +
                        'max=%s-%s' % (year, half[1]),
                    verify = False,
                    headers = {'Content-Type':'application/json'})


                drawings = response.json()
                for drawing in drawings:
                    date = drawing['field_draw_date']
                    c = db.execute('SELECT count(date) FROM %s WHERE date="%s"' % (name, date))
                    if c.fetchone()[0] == 0:
                        b = re.split(',', drawing['field_winning_numbers'])
                        db.execute('INSERT INTO %s VALUES ("%s", "%02d", "%02d", "%02d", "%02d", "%02d", "%02d")' %
                                   (name, date, int(b[0]), int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])))

db.commit()


c = db.execute("SELECT max(date) FROM %s" % name)
lt = c.fetchone()[0]
formats.append([lt])

c = db.execute("SELECT * FROM %s ORDER BY date" % name)
nb = {}
bb = {}
mn = []
for m in range(len(formats) - 1):
    mn.append(0)

print('History')
for r in c:
    print(r)

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
 
    if r[6] not in bb.keys():
        bb[r[6]] = ['', 0]
    bb[r[6]][0] = r[0]
    bb[r[6]][1] += 1

db.close()


print('\nN date')
for n in sorted(nb.items(), key=by_date, reverse=True):
    print(n)

print('\nN freq')
for n in sorted(nb.items(), key=by_freq, reverse=True):
    print(n)

print('\nb date')
for b in sorted(bb.items(), key=by_date, reverse=True):
    if b[0] <= str(formats[len(formats) - 2][2]):
        print(b)

print('\nB freq')
for b in sorted(bb.items(), key=by_freq, reverse=True):
    if b[0] <= str(formats[len(formats) - 2][2]):
        print(b)
