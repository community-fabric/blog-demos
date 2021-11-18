from ipfabric import IPFabric
from os import getenv
from pprint import pprint


if __name__ == '__main__':
    ipf = IPFabric('https://demo3.ipfabric.io/', getenv('IPF_TOKEN'))

    payload = {
        "columns": [
            "sn",
            "hostname",
            "intName",
            "siteName",
            "l1",
            "l2",
            "dscr",
            "mac",
            "duplex",
            "speed",
            "errDisabled",
            "mtu",
            "primaryIp",
        ],
        "snapshot": "$last"
    }
    interfaces = ipf.query('tables/inventory/interfaces', payload)

    pprint(interfaces[0])

"""
{'dscr': None,
 'duplex': None,
 'errDisabled': None,
 'hostname': 'L62SD24',
 'intName': 'Vl1',
 'l1': 'down',
 'l2': 'down',
 'mac': 'aabb.cc82.ff00',
 'mtu': 1500,
 'primaryIp': None,
 'siteName': 'L62',
 'sn': 'a3effa6',
 'speed': None}
"""