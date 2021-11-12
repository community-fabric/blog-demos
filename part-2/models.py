from datetime import datetime
from ipf_api_client import IPFClient
from typing import Optional


class Snapshot:
    def __init__(self, **kwargs):
        self.id: str = kwargs["id"]
        self.name: str = kwargs["name"]
        self.count: int = kwargs["totalDevCount"]
        self.loaded: bool = True if kwargs["state"] == 'loaded' else False
        self.locked: str = kwargs["locked"]
        self.start = datetime.fromtimestamp(kwargs["tsStart"] / 1000.0)
        self.end = datetime.fromtimestamp(kwargs["tsEnd"] / 1000.0)


class Table:
    def __init__(self, client: IPFClient, name: str):
        self.endpoint = name
        self.name = name.split('/')[-1]
        self.client = client

    def all(self, filters: dict = None, snapshot_id: Optional[str] = None):
        """
        Gets all data from corresponding endpoint
        :param filters: dict: Optional filters
        :param snapshot_id: str: Optional snapshot ID to override class
        :return: list: List of Dictionaries
        """
        return self.client.fetch_all(self.endpoint, filters=filters, snapshot_id=snapshot_id)


class Inventory:
    def __init__(self, client: IPFClient):
        self.sites = Table(client, '/tables/inventory/sites')
        self.devices = Table(client, '/tables/inventory/devices')
        self.models = Table(client, '/tables/inventory/summary/models')
        self.platforms = Table(client, '/tables/inventory/summary/platforms')
        self.families = Table(client, '/tables/inventory/summary/families')
        self.vendors = Table(client, '/tables/inventory/summary/vendors')
        self.part_numbers = Table(client, '/tables/inventory/pn')
        self.interfaces = Table(client, '/tables/inventory/interfaces')
