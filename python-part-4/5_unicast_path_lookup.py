from os import path

from ipfabric import IPFClient
from ipfabric_diagrams import IPFDiagram, Unicast, OtherOptions, Algorithm, EntryPoint
from ipfabric_diagrams import icmp

if __name__ == '__main__':
    # Get a couple random hosts
    ipf = IPFClient()
    host1 = ipf.inventory.hosts.all(filters={"ip": ["cidr", "10.35.0.0/16"]})[3]['ip']
    host2 = ipf.inventory.hosts.all(filters={"ip": ["cidr", "10.66.0.0/16"]})[5]['ip']

    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    print(Unicast.schema_json(indent=2))

    unicast_icmp = Unicast(
        startingPoint=host1,
        destinationPoint=host2,
        protocol='icmp',
        icmp=icmp.ECHO_REQUEST,  # Dict is also valid (may show a typing error in IDE): {'type': 0, 'code': 0}
        ttl=64,
        securedPath=False  # UI Option 'Security Rules'; True == 'Drop'; False == 'Continue'
    )

    with open(path.join('path_lookup', '5_1_unicast_icmp.png'), 'wb') as f:
        f.write(diagram.diagram_png(unicast_icmp))

    unicast_tcp = Unicast(
        startingPoint=host1,
        destinationPoint=host2,
        protocol='tcp',
        srcPorts='1024,2048-4096',
        dstPorts='80,443',
        otherOptions=OtherOptions(applications='(web|http|https)', tracked=False),
        srcRegions='US',
        dstRegions='CZ',
        ttl=64,
        securedPath=False
    )

    with open(path.join('path_lookup', '5_2_unicast_tcp.png'), 'wb') as f:
        f.write(diagram.diagram_png(unicast_tcp))

    with open(path.join('path_lookup', '5_3_unicast_tcp_swap_src_dst.png'), 'wb') as f:
        f.write(diagram.diagram_png(unicast_tcp, unicast_swap_src_dst=True))

    # Subnet Example
    unicast_subnet = Unicast(
        startingPoint='10.38.115.0/24',
        destinationPoint='10.66.126.0/24',
        protocol='tcp',
        srcPorts='1025',
        dstPorts='22',
        securedPath=False
    )

    with open(path.join('path_lookup', '5_4_unicast_subnet.png'), 'wb') as f:
        f.write(diagram.diagram_png(unicast_subnet))

    # User Defined Entry Point Example
    unicast_entry_point = Unicast(
        startingPoint='1.0.0.1',
        destinationPoint='10.66.126.0/24',
        protocol='tcp',
        srcPorts='1025',
        dstPorts='22',
        securedPath=True,
        firstHopAlgorithm=Algorithm(entryPoints=[
            EntryPoint(sn='test', iface='eth0', hostname='test'),
            dict(sn='test', iface='eth0', hostname='test')
        ])
    )

    # with open(path.join('path_lookup', '5_5_unicast_entry_point.png'), 'wb') as f:
    #     f.write(diagram.diagram_png(unicast_entry_point))
