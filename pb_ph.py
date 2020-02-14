#!/usr/bin/python -B
import json
import re
import requests

response = requests.get(
    'https://www.powerball.com/api/v1/numbers/powerball?_format=json&' +
        'min=2019-01-01&' +
        'max=2019-12-31',
    verify = False,
    headers = {'Content-Type':'application/json'})
print

drawings = json.loads(response.text)
# print(json.dumps(drawings, indent=4))

stats = { }
for n in range(1, 70):
    stats['%02d' % n] = 0

for drawing in drawings:
    numbers = re.split(',', drawing['field_winning_numbers'])
    for i in range(5):
        stats[numbers[i]] += 1

print(len(drawings))
print(json.dumps(stats, indent=4))
