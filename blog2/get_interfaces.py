from ipfabric import IPFabric
from os import getenv
from pprint import pprint
from ipf_api_client import IPFClient


if __name__ == '__main__':
    # ipf = IPFabric('https://demo3.ipfabric.io/', getenv('IPF_TOKEN'))

    ipf = IPFClient('https://demo3.ipfabric.io/')
    sites = ipf.site_list()
    devices = ipf.device_list()
    print()

    # interfaces = ipf.query('tables/inventory/interfaces')

    # pprint(interfaces[0])

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