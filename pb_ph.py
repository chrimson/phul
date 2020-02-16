#!/usr/bin/python -B
import re
import requests
import sqlite3

db = sqlite3.connect('games.db')
c = db.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pb'")
if c.fetchone()[0] == 0:
    db.execute("CREATE TABLE pb (date TEXT, b1 TEXT, b2 TEXT, b3 TEXT, b4 TEXT, b5 TEXT, b6 TEXT)")

for year in range(1997, 2021):
    for half in [('01-01', '06-30'), ('07-01', '12-31')]:
        response = requests.get(
            'https://www.game.com/api/v1/numbers/game?_format=json&' +
                'min=%s-%s&' % (year, half[0]) +
                'max=%s-%s' % (year, half[1]),
            verify = False,
            headers = {'Content-Type':'application/json'})
        
        drawings = response.json()
        for drawing in drawings:
            date = drawing['field_draw_date']
            c = db.execute("SELECT count(date) FROM pb WHERE date='%s'" % date)
            if c.fetchone()[0] != 0:
                continue
        
            b = re.split(',', drawing['field_winning_numbers'])
            db.execute("INSERT INTO pb VALUES ('%s', '%02d', '%02d', '%02d', '%02d', '%02d', '%02d')" %
                           (date, int(b[0]), int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])))

db.commit()
db.close()
