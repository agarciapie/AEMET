import requests

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/"

querystring = {"api_key":"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZ2FyY2lhcGllQGdtYWlsLmNvbSIsImp0aSI6ImZiMTQxYWY0LTQ1MzMtNDc5NS1hNTM5LTM0Mjk4NzNjMGNlOSIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzM4NTMwNjI0LCJ1c2VySWQiOiJmYjE0MWFmNC00NTMzLTQ3OTUtYTUzOS0zNDI5ODczYzBjZTkiLCJyb2xlIjoiIn0.GeKTxZLkTsGluLYZUjxZrMBG41K78-kq7b9JVHLF9I8"}

headers = {
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)
json_data = response.json()

keys_data = json_data.keys()
value_data = json_data.values()

print(keys_data)
print(value_data)

















