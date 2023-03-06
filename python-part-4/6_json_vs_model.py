from ipfabric_diagrams import IPFDiagram, Unicast, OtherOptions
from ipfabric_diagrams.output_models.graph_result import GraphResult

if __name__ == '__main__':
    diagram = IPFDiagram()  # IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)

    unicast_tcp = Unicast(
        startingPoint='10.47.117.112',
        destinationPoint='10.66.127.116',
        protocol='tcp',
        srcPorts=1025,
        dstPorts='80,443',
        otherOptions=OtherOptions(applications='http|web'),
        securedPath=True  # Must be set to True or 'passingTraffic' attribute will always return 'all'
    )

    json_data = diagram.diagram_json(unicast_tcp, snapshot_id='$last')

    model_data = diagram.diagram_model(unicast_tcp, snapshot_id='$last')

    print(GraphResult.schema_json(indent=2))
