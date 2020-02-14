#!/usr/bin/python -B
import json
import requests

payload = '{pageSize: 403, startDate: "02/04/2010", endDate: "03/04/2020", pageNumber: 3 }'

#response = requests.get('https://www.powerball.com/api/v1/numbers/powerball?_format=json&min=1996-06-01%2000:00:00&max=1997-11-03%2000:00:00',
response = requests.post('https://www.megamillions.com/cmspages/utilservice.asmx/GetDrawingPagingData',
                         verify = False,
                         headers = {'Content-Type':'application/json'},
                         data = payload)
print

j = json.loads(response.text)
#print(json.dumps(j, indent=4))

data = j['d']
j2 = json.loads(data)
print(json.dumps(j2, indent=4))
