from typing import Optional, Union

from requests import Session
from urllib.parse import urljoin


class IPFabric(Session):
    def __init__(self, base_url: str, token: str, verify: bool = True, api_version: str = "v1"):
        """
        Initiate IPFabric session
        :param base_url: str: https://your_instance.ipfabric.io
        :param token: str: Your API Token
        :param verify: bool: False to ignore certificate verification
        :param api_version: str: Default to v1 the current version
        """
        super(IPFabric, self).__init__()
        self.base_url = urljoin(urljoin(base_url, "api/"), api_version + '/')
        self.headers.update({'Content-Type': 'application/json', 'X-API-Token': token})
        self.verify = verify

    def query(self, endpoint: str, payload: dict):
        """
        Submits the query against IP Fabric and returns a list of dictionaries
        :param endpoint: str: Example: tables/inventory/sites
        :param payload: dict: See the API documentation in IP Fabric for the json to post
        :return: list[dict]: List of dictionaries of your data
        """
        return self._ipf_pager(urljoin(self.base_url, endpoint), payload)

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
        :param limit: int: Limit of number of entries to return in one call
        :param start: int: Where to start for the data
        :return: list: List of dictionaries
        """
        data = list() if not data else data

        payload["pagination"] = dict(
            limit=limit,
            start=start
        )
        r = self.post(url, json=payload)
        r.raise_for_status()
        r = r.json()
        data.extend(r['data'])
        if limit + start < r["_meta"]["count"]:
            self._ipf_pager(url, payload, data, limit, start+limit)
        return data
