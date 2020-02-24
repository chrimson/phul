#!/usr/bin/python -B
import json
import requests

for pg in range(1,4):
  payload = '{pageSize: 403, startDate: "01/21/2009", endDate: "03/04/2020", pageNumber: %s }' % str(pg)

  response = requests.post('https://www.megamillions.com/cmspages/utilservice.asmx/GetDrawingPagingData',
                           verify = False,
                           headers = {'Content-Type':'application/json'},
                           data = payload)

  data = response.json()
  jstr = data['d']
  drawings = json.loads(jstr)['DrawingData']
  #print(json.dumps(drawings, indent=4))


  for pd in drawings:
    print(pd['PlayDate'])
