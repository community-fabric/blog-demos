from os import path

from ipfabric_diagrams import IPFDiagram, Multicast

if __name__ == '__main__':
    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    multicast = Multicast(
        source='10.33.230.2',
        group='233.1.1.1',
        receiver='10.33.244.200',
        protocol='tcp',
        srcPorts='1024,2048-4096',
        dstPorts='80,443',
    )

    with open(path.join('path_lookup', '7_multicast.png'), 'wb') as f:
        f.write(diagram.diagram_png(multicast))
    