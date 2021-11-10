from ipfabric import IPFabric
from os import getenv
from pprint import pprint


if __name__ == '__main__':
    ipf = IPFabric('https://demo3.ipfabric.io/', getenv('IPF_TOKEN'))

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
    sites = ipf.query('tables/inventory/sites', payload)

    pprint(sites[0])

"""
{'devicesCount': 22,
 'id': '1111118694',
 'networksCount': 61,
 'rDCount': 3,
 'routersCount': 6,
 'siteKey': '1111118694',
 'siteName': 'HWLAB',
 'stpDCount': 2,
 'switchesCount': 8,
 'usersCount': 13,
 'vlanCount': 131}
"""