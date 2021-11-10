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
    sites = ipf.query('api/v1/tables/inventory/sites', payload)

    pprint(sites[0])

