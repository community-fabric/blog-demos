import requests

session = requests.Session()
session.headers.update({'Content-Type': 'application/json', 'X-API-Token': 'TOKEN'})

payload = {
    "columns": [
        "id",
        "siteName",
        "siteKey",
        "devicesCount",
        "usersCount",
        "stpDCount",
        "switchesCount",
        "vlanCount",
        "rDCount",
        "routersCount",
        "networksCount"
    ],
    "snapshot": "$last"
}
r = session.post('https://demo3.ipfabric.io/api/v1/tables/inventory/sites', json=payload)
print(r.json()['data'][0])
