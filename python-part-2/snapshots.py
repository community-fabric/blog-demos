"""
snapshot.py
"""
from ipfabric import IPFClient
from pprint import pprint


if __name__ == '__main__':
    ipf = IPFClient('https://demo3.ipfabric.io/', snapshot_id="$lastLocked")

    print(f"IP Fabric version: {ipf.os_version}")
    """
    IP Fabric version: 4.0.2
    """

    print(f"Class snapshot id is set to {ipf.snapshot_id}")
    print(f"Latest snapshot id is \t\t{ipf.snapshots['$last'].id}")
    """
    Class snapshot id is set to d3bd033e-1ba6-4b27-86f5-18824a1a495e
    Latest snapshot id is	    c8684ea9-dfd8-400d-a4b8-ba1c4bc7c185
    """

    print("Print a snapshot object: ")
    pprint(ipf.snapshots[ipf.snapshot_id].__dict__)
    """
    Print a snapshot object: 
    {'count': 640,
     'end': datetime.datetime(2021, 10, 21, 12, 37, 3, 513000),
     'id': 'd3bd033e-1ba6-4b27-86f5-18824a1a495e',
     'loaded': True,
     'locked': True,
     'name': 'Baseline 10-21',
     'start': datetime.datetime(2021, 10, 21, 11, 59, 54, 941000)}
    """
