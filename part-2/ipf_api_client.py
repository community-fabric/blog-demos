import os
import re
from collections import OrderedDict
from typing import Optional, Union
from urllib.parse import urljoin, urlparse

from httpx import Client as httpxClient


def check_url(func):
    """
    Checks to make sure api/v1/ is not in the URL
    """
    def wrapper(self, url, *args, **kwargs):
        path = urlparse(url or kwargs["url"]).path
        url = path.split('v1/')[1] if 'v1/' in path else path
        return func(self, url, *args, **kwargs)
    return wrapper


class IPFClient(httpxClient):
    def __init__(
            self,
            base_url: Optional[str] = None,
            token: Optional[str] = None,
            snapshot_id: str = "$last",
            *vargs,
            **kwargs
    ):
        """
        Initializes the IP Fabric Client
        :param base_url: str: IP Fabric instance provided in 'base_url' parameter, or the 'IPF_URL' environment variable
        :param token: str: API token or 'IPF_TOKEN' environment variable
        :param snapshot_id: str: IP Fabric snapshot ID to use by default for database actions - defaults to '$last'
        :param vargs:
        :param kwargs:
        """
        try:
            base_url = urljoin(base_url or os.environ["IPF_URL"], "api/v1/")
        except KeyError:
            raise RuntimeError(f"IP Fabric base_url not provided or IPF_URL not set")

        try:
            token = token or os.environ["IPF_TOKEN"]
        except KeyError:
            raise RuntimeError(f"IP Fabric token not provided or IPF_TOKEN not set")

        super().__init__(base_url=base_url, *vargs, **kwargs)
        self.headers.update({'Content-Type': 'application/json', 'X-API-Token': token})

        # Request IP Fabric for the OS Version, by doing that we are also ensuring the token is valid
        self.os_version = self.fetch_os_version()
        self.snapshots = self.get_snapshots()
        self.snapshot_id = snapshot_id
        self.inventory = Inventory(self)

    @property
    def snapshot_id(self):
        return self._snapshot_id

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        if snapshot_id in ["$last", None]:
            # If no snapshot then use last and convert it to an ID
            self._snapshot_id = self._fetch_snapshot_id()
        elif snapshot_id == "$prev":
            self._snapshot_id = self._fetch_snapshot_id(prev=True)
        elif snapshot_id == "$lastLocked":
            self._snapshot_id = self._fetch_snapshot_id(locked=True)
        elif snapshot_id not in self.snapshots:
            # Verify snapshot ID is valid
            raise ValueError(f"##ERROR## EXIT -> Incorrect Snapshot ID: '{snapshot_id}'")
        else:
            self._snapshot_id = snapshot_id

    def fetch_os_version(self):
        """
        Gets IP Fabric version to ensure token is correct
        :return: str: IP Fabric version
        """
        res = self.get(url="os/version")
        if not res.is_error:
            try:
                return res.json()["version"]
            except KeyError as exc:
                raise ConnectionError(f"Error While getting the OS version, no Version available, message: {exc.args}")
        else:
            raise ConnectionRefusedError("Verify URL and Token are correct.")

    def get_snapshots(self):
        """
        Gets all snapshots from IP Fabric and returns a dictionary of {ID: Snapshot_info}
        :return: dict[str, dict]: Dictionary with ID as key and dictionary with info as the value
        """
        res = self.get("/snapshots")
        res.raise_for_status()

        snap_dict = OrderedDict()
        for s in res.json():
            snap_dict[s["id"]] = {
                "id": s["id"],
                "name": s["name"],
                "count": s["totalDevCount"],
                "state": s["state"],
                "locked": s["locked"]
            }

        return snap_dict

    def _fetch_snapshot_id(self, prev: bool = False, locked: bool = False):
        """
        Method to get Last Loaded snapshot
        :param prev: bool: If True it will get the 2nd latest snapshot
        :param locked: bool: If True it will get the latest locked snapshot
        :return: str: Snapshot ID
        """
        snapshots = self.snapshots.values()
        s_iter = iter(snapshots)

        if locked:
            try:
                return next((s["id"] for s in s_iter if s['state'] == 'loaded' and s["locked"]))
            except StopIteration:
                raise ValueError("No loaded locked snapshots found on IP Fabric.")

        snapshot = next((s["id"] for s in s_iter if s['state'] == 'loaded'))
        if prev:
            return next((s["id"] for s in s_iter if s['state'] == 'loaded'))
        else:
            return snapshot

    @check_url
    def fetch(
        self,
        url,
        columns: Optional[list[str]] = None,
        filters: Optional[dict] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
    ):
        """
        Gets data from IP Fabric for specified endpoint
        :param url: str: Example tables/vlan/device-summary
        :param columns: list: Optional list of columns to return, None will return all
        :param filters: dict: Optional dictionary of filters
        :param limit: int: Default to 1,000 rows
        :param start: int: Starts at 0
        :param snapshot_id: str: Optional snapshot_id to override default
        :return: list: List of Dictionary objects.
        """

        payload = dict(
            columns=columns or self._get_columns(url),
            snapshot=snapshot_id or self.snapshot_id,
            pagination=dict(
                start=start,
                limit=limit
            )
        )
        if filters:
            payload["filters"] = filters

        res = self.post(url, json=payload)
        res.raise_for_status()
        return res.json()["data"]

    @check_url
    def fetch_all(
            self,
            url: str,
            columns: Optional[list[str]] = None,
            filters: Optional[dict] = None,
            snapshot_id: Optional[str] = None,
    ):
        """
        Gets all data from IP Fabric for specified endpoint
        :param url: str: Example tables/vlan/device-summary
        :param columns: list: Optional list of columns to return, None will return all
        :param filters: dict: Optional dictionary of filters
        :param snapshot_id: str: Optional snapshot_id to override default
        :return: list: List of Dictionary objects.
        """

        payload = dict(columns=columns or self._get_columns(url), snapshot=snapshot_id or self.snapshot_id)
        if filters:
            payload["filters"] = filters

        return self._ipf_pager(url, payload)

    @check_url
    def query(self, url: str, params: Union[str, dict]):
        """
        Submits a query, does no formating on the parameters.  Use for copy/pasting from the webpage
        :param url: str: Example: https://demo1.ipfabric.io/api/v1/tables/vlan/device-summary
        :param params: Union[str, dict]: JSON object to submit in POST, can be string read from file.
        :return: list: List of Dictionary objects.
        """
        if isinstance(params, dict):
            res = self.post(url, json=params)
        else:
            res = self.post(url, data=params)
        res.raise_for_status()
        return res.json()["data"]

    def _get_columns(self, url: str):
        """
        Submits malformed payload and extracts column names from it
        :param url: str: API url to post
        :return: list: List of column names
        """
        r = self.post(url, json=dict(snapshot=self.snapshot_id, columns=["*"]))
        if r.status_code == 422:
            msg = r.json()["errors"][0]["message"]
            return [x.strip() for x in re.match(r'".*".*\[(.*)\]$', msg).group(1).split(',')]
        else:
            r.raise_for_status()

    def _ipf_pager(
            self,
            url: str,
            payload: dict,
            data: Optional[Union[list, None]] = None,
            limit: int = 10000,
            start: int = 0
    ):
        """
        Loops through and collects all the data from the tables
        :param url: str: Full URL to post to
        :param payload: dict: Data to submit to IP Fabric
        :param data: list: List of data to append subsequent calls
        :param start: int: Where to start for the data
        :return: list: List of dictionaries
        """
        data = data or list()

        payload["pagination"] = dict(
            limit=limit,
            start=start
        )
        r = self.post(url, json=payload)
        r.raise_for_status()
        r = r.json()
        data.extend(r['data'])
        if limit + start < r["_meta"]["count"]:
            self._ipf_pager(url, payload, data, start+limit)
        return data


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
