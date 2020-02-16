#!/usr/bin/python -B
import json
import requests

payload = '{pageSize: 403, startDate: "01/21/2010", endDate: "03/04/2020", pageNumber: 3 }'

response = requests.post('https://www.game.com/cmspages/utilservice.asmx/GetDrawingPagingData',
                         verify = False,
                         headers = {'Content-Type':'application/json'},
                         data = payload)

data = response.json()
jstr = data['d']
drawings = json.loads(jstr)
