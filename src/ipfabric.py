from typing import Optional, Union

from requests import Session
from urllib.parse import urljoin


class IPFabric(Session):
    def __init__(self, base_url: str, token: str, verify: bool = False):
        super(IPFabric, self).__init__()
        self.base_url = base_url
        self.headers.update({'Content-Type': 'application/json', 'X-API-Token': token})
        self.verify = verify

    def query(self, endpoint: str, payload: dict):
        return self._ipf_pager(urljoin(self.base_url, endpoint), payload)

    def _ipf_pager(
            self,
            endpoint: str,
            payload: dict,
            data: Optional[Union[list, None]] = None,
            limit: int = 1000,
            start: int = 0
    ):
        data = list() if not data else data

        payload["pagination"] = dict(
            limit=limit,
            start=start
        )
        r = self.post(endpoint, json=payload)
        r.raise_for_status()
        r = r.json()
        data.extend(r['data'])
        if limit + start < r["_meta"]["count"]:
            self._ipf_pager(endpoint, payload, data, limit, start+limit)
        return data
