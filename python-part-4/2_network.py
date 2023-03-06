from os import path

from ipfabric_diagrams import IPFDiagram, Network, Layout

if __name__ == '__main__':
    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    with open(path.join('network', '2_1_network.png'), 'wb') as f:
        f.write(diagram.diagram_png(Network(sites='MPLS', all_network=True)))

    with open(path.join('network', '2_2_network.png'), 'wb') as f:
        f.write(diagram.diagram_png(Network(sites=['LAB01', 'HWLAB'], all_network=False)))

    with open(path.join('network', '2_3_network.png'), 'wb') as f:
        f.write(diagram.diagram_png(
            Network(sites='L71', all_network=False, layouts=[Layout(path='L71', layout='upwardTree')])
        ))
