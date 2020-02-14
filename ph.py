#!/usr/bin/python -B
import re
import requests

# from urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(category = InsecureRequestWarning)

response = requests.get('https://www.google.com',
                        verify = False,
                        headers = {'Content-Type':'application/json'})

f = re.findall('google', response.text)

print
print(f)
