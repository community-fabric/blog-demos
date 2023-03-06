from os import path

from ipfabric import IPFClient
from ipfabric_diagrams import IPFDiagram, Network, Overlay

if __name__ == '__main__':
    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    with open(path.join('network', '3_1_network_snap_overlay.png'), 'wb') as f:
        f.write(diagram.diagram_png(Network(sites='MPLS', all_network=False),
                                    overlay=Overlay(snapshotToCompare='$prev')))

    # Get intent rule ID
    ipf = IPFClient()
    ipf.intent.load_intent()
    intent_rule_id = ipf.intent.intent_by_name['NTP Reachable Sources'].intent_id

    with open(path.join('network', '3_2_network_intent_overlay.png'), 'wb') as f:
        f.write(diagram.diagram_png(Network(sites=['L71'], all_network=False),
                                    overlay=Overlay(intentRuleId=intent_rule_id)))

    