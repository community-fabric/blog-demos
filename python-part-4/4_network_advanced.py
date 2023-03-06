from os import path

from ipfabric import IPFClient
from ipfabric_diagrams import IPFDiagram, Network, NetworkSettings, Layout

if __name__ == '__main__':
    # Get a list of sites
    sites = IPFClient().inventory.sites.all(columns=['siteName'], filters={"and": [{"siteName": ["reg", "^L\\d"]}]})
    sites = [s['siteName'] for s in sites]

    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    mpls_settings = NetworkSettings()
    mpls_settings.hide_group('layer 1')
    mpls_settings.hide_protocol('rib')
    mpls_settings.hiddenDeviceTypes.append('cloud')
    with open(path.join('network', '4_1_network_advanced_mpls.png'), 'wb') as f:
        f.write(diagram.diagram_png(
            Network(sites='MPLS', all_network=False, layouts=[Layout(path='MPLS', layout='radial')]),
            graph_settings=mpls_settings
        ))

    ospf_settings = NetworkSettings()
    ospf_settings.hide_all_protocols()
    ospf_settings.hide_protocol('ospf', unhide=True)
    ospf_settings.ungroup_protocol('ospf')
    ospf_settings.change_label('ospf', 'subnet')

    bgp_settings = NetworkSettings()
    bgp_settings.hide_all_protocols()
    bgp_settings.hide_protocol('ebgp', unhide=True)
    bgp_settings.hide_protocol('ibgp', unhide=True)

    for site in sites:
        with open(path.join('network/ospf', f'{site}_ospf.png'), 'wb') as f:
            f.write(diagram.diagram_png(Network(sites=site, all_network=False), graph_settings=ospf_settings))

        with open(path.join('network/bgp', f'{site}_bgp.svg'), 'wb') as f:
            f.write(diagram.diagram_svg(Network(sites=site, all_network=False), graph_settings=bgp_settings))
