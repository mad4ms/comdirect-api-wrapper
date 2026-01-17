import json
import requests
from .exceptions import ApiError
from .utils import timestamp


class ComdirectHttpClient:
    def __init__(self, base_url: str, session):
        self._base_url = base_url
        self._session = session

    def request(self, method: str, path: str, *, headers=None, params=None, json_data=None):
        hdrs = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._session.token()}",
            "x-http-request-info": json.dumps(
                {
                    "clientRequestId": {
                        "sessionId": self._session.session_id,
                        "requestId": timestamp(),
                    }
                }
            ),
        }
        if headers:
            hdrs.update(headers)

        response = requests.request(
            method,
            self._base_url + path,
            headers=hdrs,
            params=params,
            json=json_data,
            allow_redirects=False,
        )

        if response.status_code >= 400:
            raise ApiError(response)

        return response
