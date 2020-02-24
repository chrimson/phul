#!/usr/bin/python -B

# Random Heuristic Ordering

import datetime as dt
import json
import random
import re
import requests
import sqlite3
import sys
import urllib3

def to_date(ds):
    return dt.date(int(ds[0:4]), int(ds[5:7]), int(ds[8:10]))

def by_date(item):
    return item[1][0]

def by_freq(item):
    return item[1][1]


if len(sys.argv) != 2:
    print('Need sequence name')
    exit()
name = sys.argv[1]

try:
    config = json.load(open('rho.json', 'r'))
    fmt = config['formats'][re.sub('^sim_(.*)', '\\1', name)]
except:
    print('No valid configuration found')
    exit()

db = sqlite3.connect('rho.db')
c = db.execute('SELECT count(name) FROM sqlite_master ' +
                   'WHERE type="table" AND name="%s"' % name)
if c.fetchone()[0] == 0:
    db.execute('CREATE TABLE %s (date, b1, b2, b3, b4, b5, b6)' % name)

if name.startswith('sim_'):
    days = 4
    for f in range(len(fmt)):

        date = to_date(fmt[f][0])
        if f + 1 < len(fmt):
            next_fmt = to_date(fmt[f + 1][0])
        else:
            next_fmt = dt.date.today() + dt.timedelta(1)

        while date < next_fmt:
            sb = []
            for n in range(0, 5):
                sb.append('"%02d"' % random.randint(1, fmt[f][1]))
            sb.append('"%02d"' % random.randint(1, fmt[f][2]))
            bs = ','.join(sb)

            c = db.execute('SELECT count(date) FROM %s WHERE date="%s"' % (name, date))
            if c.fetchone()[0] == 0:
                db.execute('INSERT INTO %s VALUES ("%s", %s)' % (name, date, bs))

            date += dt.timedelta(days)
            days = 4 if days == 3 else 3

else:
    c = db.execute('SELECT max(date) FROM %s' % name)
    lt = c.fetchone()[0]
    if lt is None:
        lt = fmt[0][0]
    last = to_date(lt)
    today = dt.date.today()
    yr0 = last.year
    yr1 = today.year

    if (today - last).days > 2:
        urllib3.disable_warnings()
        try:
            for year in range(yr0, yr1 + 1):
                for half in [('01-01', '06-30'), ('07-01', '12-31')]:
                    response = requests.get(
                        'https://www.%s.com/api/v1/numbers/%s?_format=json&' %
                        (name, name) +
                            'min=%s-%s&' % (year, half[0]) +
                            'max=%s-%s' % (year, half[1]),
                        verify = False,
                        headers = {'Content-Type':'application/json'})

                    drawings = response.json()
                    for drawing in drawings:
                        date = drawing['field_draw_date']
                        c = db.execute('SELECT count(date) FROM %s ' % name +
                                           'WHERE date="%s"' % date)
                        if c.fetchone()[0] == 0:
                            b = re.split(',', drawing['field_winning_numbers'])
                            db.execute('INSERT INTO %s VALUES ' +
                                           '("%s", "%02d", ' % (name, date) + 
                                           '"%02d", "%02d", "%02d", "%02d", "%02d")' %
                                           (int(b[0]),
                                            int(b[1]),
                                            int(b[2]),
                                            int(b[3]),
                                            int(b[4]),
                                            int(b[5])))
        except:
            try:
                for year in range(yr0, yr1 + 1):
                    payload = '''{
                                     pageSize: 108,
                                     startDate: "%s/%s",
                                     endDate: "%s/%s",
                                     pageNumber: 1
                                 }''' % ('01/01', year, '12/31', year)
                    response = requests.post(
                        'https://www.%s.com/cmspages/utilservice.asmx/' +
                            'GetDrawingPagingData' % name,
                        verify = False,
                        headers = {'Content-Type':'application/json'},
                        data = payload)
                    drawings = json.loads(response.json()['d'])['DrawingData']
                
                    for drawing in drawings:
                        date = drawing['PlayDate'][0:10]
                        c = db.execute('SELECT count(date) FROM %s ' % name +
                                           'WHERE date="%s"' % date)
                        if c.fetchone()[0] == 0:
                            db.execute('INSERT INTO %s VALUES ' +
                                           '("%s", "%02d", ' % (name, date) +
                                           '"%02d", "%02d", "%02d", "%02d", "%02d")' %
                                       (drawing['N1'],
                                        drawing['N2'],
                                        drawing['N3'],
                                        drawing['N4'],
                                        drawing['N5'],
                                        drawing['MBall']))
 
            except:
                print('Problem with connection')
                exit()

db.commit()


c = db.execute('SELECT max(date) FROM %s' % name)
lt = c.fetchone()[0]
fmt.append([lt])

c = db.execute('SELECT * FROM %s ORDER BY date' % name)
nb = {}
bb = {}
mn = []
mb = []
for m in range(len(fmt) - 1):
    mn.append(0)
    mb.append(0)

print('History')
for r in c:
    print(r)

    for f in range(1, len(fmt) - 1):
        if r[0] == fmt[f][0]:
            for n in nb.items():
                mn[f] = n[1][1] if n[1][1] < mn[f] or mn[f] == 0 else mn[f]
            for b in bb.items():
                mb[f] = b[1][1] if b[1][1] < mb[f] or mb[f] == 0 else mb[f]

        if r[0] == fmt[f + 1][0]:
            for n in range(fmt[f - 1][1] + 1, fmt[f][1] + 1):
                nb['%02d' % n][1] += mn[f]
            for b in range(fmt[f - 1][2] + 1, fmt[f][2] + 1):
                bb['%02d' % b][1] += mb[f]
 
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
    if n[0] <= str(fmt[len(fmt) - 2][1]):
        print(n)

print('\nN freq')
for n in sorted(nb.items(), key=by_freq, reverse=True):
    if n[0] <= str(fmt[len(fmt) - 2][1]):
        print(n)

print('\nB date')
for b in sorted(bb.items(), key=by_date, reverse=True):
    if b[0] <= str(fmt[len(fmt) - 2][2]):
        print(b)

print('\nB freq')
for b in sorted(bb.items(), key=by_freq, reverse=True):
    if b[0] <= str(fmt[len(fmt) - 2][2]):
        print(b)
