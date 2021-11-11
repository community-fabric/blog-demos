import os
import re
from collections import OrderedDict
from typing import Optional, Union
from urllib.parse import urljoin

from httpx import Client as httpxClient


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
            base_url = base_url or os.environ["IPF_URL"]
            base_url = urljoin(base_url, "api/v1/")
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

    @property
    def snapshot_id(self):
        return self._snapshot_id

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        if snapshot_id in ["$last", None]:
            # If no snapshot then use last and convert it to an ID
            self._snapshot_id = self.fetch_snapshot_id()
        elif snapshot_id == "$prev":
            self._snapshot_id = self.fetch_snapshot_id(prev=True)
        elif snapshot_id == "$lastLocked":
            self._snapshot_id = self.fetch_snapshot_id(locked=True)
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

    def fetch_snapshot_id(self, prev: bool = False, locked: bool = False):
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

    def site_list(
        self,
        filters: Optional[dict] = None,
        pagination: Optional[dict] = None,
        snapshot_id: Optional[str] = None,
    ):
        """
        Method to fetch the list of sites from the IPF instance opened in the API client
        :param filters: [optional] dictionary describing the table filters to be applied to the records
        :param pagination: [optional] start and length of the "page" of data required
        :param snapshot_id: [optional] IP Fabric snapshot identifier to override the default
        :return: list: List of Site dictionaries
            [
                {
                    'siteName': descriptive site name,
                    'id': site id,
                    'siteKey': site Key,
                    'devicesCount': number of devices in this site,
                }
            ]
        """
        sites = self.fetch_table(
            "tables/inventory/sites",
            columns=["siteName", "id", "siteKey", "devicesCount"],
            filters=filters,
            pagination=pagination,
            snapshot_id=snapshot_id or self.snapshot_id,
        )
        return sites

    def device_list(
        self,
        filters: Optional[dict] = None,
        pagination: Optional[dict] = None,
        snapshot_id: Optional[str] = None,
    ):
        """
        Method to fetch the list of devices from the IPF instance opened in the API client, or the one entered
        Takes parameters to select:
        * filters - [optional] dictionary describing the table filters to be applied to the records (taken from IP Fabric table description)
        * pagination - [optional] start and length of the "page" of data required
        * snapshot_id - [optional] IP Fabric snapshot identifier to override the default defined at object initialisation
        Returns a list of dictionaries in the form:
        [
            {
                'hostname': device hostname,
                'siteName': name of the site where the device belongs,
                'loginIp': IP used for IP Fabric to login to this device,
                'loginType': method used to connect to the device,
                'vendor': vendor for this device,
                'platform': platform of this device,
                'family': family of this device,
                'version': OS version running on this device,
                'sn': Serial Number of the device,
                'devType': Type of device,
            }
        ]
        """

        devices = self.fetch_table(
            "tables/inventory/devices",
            columns=[
                "hostname",
                "siteName",
                "loginIp",
                "loginType",
                "vendor",
                "platform",
                "family",
                "version",
                "sn",
                "devType",
            ],
            filters=filters,
            pagination=pagination,
            snapshot_id=snapshot_id or self.snapshot_id,
        )
        return devices

    def fetch_table(
        self,
        url,
        columns: Optional[list[str]] = None,
        filters: Optional[dict] = None,
        pagination: Optional[dict] = None,
        snapshot_id: Optional[str] = None,
    ):
        """
        Method to fetch data from IP Fabric tables.
        Takes parameters to select:
        * url - [mandatory] a string containing the API endpoint for the table to be queried
        * columns - [mandatory] a list of strings describing which data is required as output
        * filters - [optional] dictionary describing the table filters to be applied to the records (taken from IP Fabric table description)
        * pagination - [optional] start and length of the "page" of data required
        * snapshot_id - [optional] IP Fabric snapshot identifier to override the default defined at object initialisation
        Returns JSON describing a dictionary containing the records required.
        """

        payload = dict(columns=columns or self._get_columns(url), snapshot=snapshot_id or self.snapshot_id)
        if filters:
            payload["filters"] = filters

        if pagination:
            payload["pagination"] = pagination

        res = self.post(url, json=payload)
        res.raise_for_status()
        body = res.json()
        return body["data"]

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
