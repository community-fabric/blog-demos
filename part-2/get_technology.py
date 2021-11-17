"""
get_technology.py
"""
from ipf_api_client import IPFClient
from pprint import pprint


if __name__ == '__main__':
    ipf = IPFClient('https://demo3.ipfabric.io/')

    wc = ipf.fetch_all('tables/wireless/controllers')
    """
    Also acceptable:
    wc = ipf.fetch_all('https://demo3.ipfabric.io/api/v1/tables/wireless/controllers')
    wc = ipf.fetch_all('/api/v1/tables/wireless/controllers')
    """
    print(f"Wireless Controllers Count: {len(wc)}")
    pprint(wc[0])
    """
    Wireless Controllers Count: 3
    {'apCount': 0,
     'clientCount': 0,
     'controller': 'HWLAB-WLC-C4400',
    ...}
    """
    print()

    arp = ipf.fetch('tables/addressing/arp', limit=1, start=0, snapshot_id='$prev')
    pprint(arp)
    """
    [{'hostname': 'HWLAB-CKP-E-1',
      'id': '11490504891149050698',
      'intName': 'LAN1',
      'ip': '10.64.128.1',
      ...}]
    """
    print()

    data = {
        "columns": [
            "id",
            "sn",
            "hostname",
            "siteKey",
            "siteName",
            "totalVlanCount",
            "activeVlanCount"
        ],
        "filters": {},
        "pagination": {
            "limit": 32,
            "start": 0
        },
        "snapshot": "d3bd033e-1ba6-4b27-86f5-18824a1a495e",
        "reports": "/technology/vlans/device-summary"
    }
    vlans = ipf.query('tables/vlan/device-summary', data)
    pprint(vlans[0])
    """
    {'activeVlanCount': 11,
     'hostname': 'L34AC11',
     'id': '1119052963',
     'siteKey': '885963458',
     'siteName': 'L34',
     'sn': 'a22ff89',
     'totalVlanCount': 15}
    """
    print()

    with open('ospf.json', 'r') as f:
        ospf = ipf.query('tables/networks/routes', f.read())
    pprint(ospf[0])
    """
    {'hostname': 'L1R16',
     'id': '1118750250',
     'network': '10.71.0.0/16',
     'nexthop': [{'ad': 150,
                  'age': 773086,
                  'intName': 'ge-0/0/2.0',
                  ...}],
     'nhCount': 1,
     ...}
    """