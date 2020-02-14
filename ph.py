#!/usr/bin/python -B
import json
import requests

response = requests.get('https://www.powerball.com/api/v1/numbers/powerball?_format=json&min=1990-01-14%2000:00:00&max=2014-02-14%2000:00:00',
                        verify = False,
                        headers = {'Content-Type':'application/json'})
print

j = json.loads(response.text)
print(json.dumps(j, indent=4))
