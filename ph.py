#!/usr/bin/python -B
import json
import requests

payload = '{pageSize: 20, startDate: "10/01/2019", endDate: "11/14/2019", pageNumber: 1 }'

#response = requests.get('https://www.powerball.com/api/v1/numbers/powerball?_format=json&min=1990-01-14%2000:00:00&max=2014-02-14%2000:00:00',
response = requests.post('https://www.megamillions.com/cmspages/utilservice.asmx/GetDrawingPagingData',
                         verify = False,
#                        headers = {'Content-Type':'application/json'})
                         data = payload,
                         headers = {'content-type':'application/json; charset=UTF-8',
                                    'referer':'https://www.megamillions.com/Winning-Numbers/Previous-Drawings.aspx?pageNumber=1&pageSize=20&startDate=10/01/2019&endDate=11/14/2019'})
print

j = json.loads(response.text)
print(json.dumps(j, indent=4))
