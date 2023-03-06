from os import path

from ipfabric import IPFClient
from ipfabric_diagrams import IPFDiagram, Host2GW

if __name__ == '__main__':
    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    # Get Random Host
    host = IPFClient().inventory.hosts.all(filters={"ip": ["cidr", "10.35.0.0/16"]})[3]['ip']

    with open(path.join('path_lookup', '1_host2gateway.png'), 'wb') as f:
        f.write(diagram.diagram_png(Host2GW(startingPoint=host)))
