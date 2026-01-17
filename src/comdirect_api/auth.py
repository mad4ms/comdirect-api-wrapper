import base64
import json
import uuid
import requests

from .exceptions import AuthenticationError, TanError
from .utils import timestamp


class Authenticator:
    TOKEN_URL = "https://api.comdirect.de/oauth/token"
    SESSION_URL = "https://api.comdirect.de/api/session/clients/user/v1/sessions"

    def __init__(
        self,
        username,
        password,
        client_id,
        client_secret,
        *,
        photo_tan_cb,
        sms_tan_cb,
        push_tan_cb,
    ):
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._photo_cb = photo_tan_cb
        self._sms_cb = sms_tan_cb
        self._push_cb = push_tan_cb

    def authenticate(self):
        token = self._primary_token()
        session_id = self._create_session(token)
        self._validate_session(token, session_id)
        return session_id, self._secondary_token(token)

    def _primary_token(self):
        r = requests.post(
            self.TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "username": self._username,
                "password": self._password,
                "grant_type": "password",
            },
        )
        if r.status_code != 200:
            raise AuthenticationError("Primary OAuth failed")
        return r.json()["access_token"]

    def _create_session(self, token):
        r = requests.get(
            self.SESSION_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "x-http-request-info": json.dumps(
                    {
                        "clientRequestId": {
                            "sessionId": str(uuid.uuid4()),
                            "requestId": timestamp(),
                        }
                    }
                ),
            },
        )
        if r.status_code != 200:
            raise AuthenticationError(f"Session creation failed: {r.status_code}")
        return r.json()[0]["identifier"]

    def _validate_session(self, token, session_id):
        request_info = json.dumps(
            {
                "clientRequestId": {
                    "sessionId": session_id,
                    "requestId": timestamp(),
                }
            }
        )
        r = requests.post(
            f"{self.SESSION_URL}/{session_id}/validate",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-http-request-info": request_info,
            },
            json={
                "identifier": session_id,
                "sessionTanActive": True,
                "activated2FA": True,
            },
        )
        if r.status_code != 201:
            raise AuthenticationError(f"Session validation failed: {r.status_code}")

        auth_info = json.loads(r.headers["x-once-authentication-info"])
        tan = self._resolve_tan(auth_info)

        r2 = requests.patch(
            f"{self.SESSION_URL}/{session_id}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "x-http-request-info": request_info,
                "x-once-authentication-info": json.dumps({"id": auth_info["id"]}),
                "x-once-authentication": tan,
                "Content-Type": "application/json",
            },
            json={
                "identifier": session_id,
                "sessionTanActive": True,
                "activated2FA": True,
            },
        )

        if r2.status_code != 200:
            raise AuthenticationError(f"TAN confirmation failed: {r2.status_code}")

    def _resolve_tan(self, info):
        typ = info["typ"]
        if typ == "P_TAN":
            return self._photo_cb(base64.b64decode(info["challenge"]))
        if typ == "M_TAN":
            return self._sms_cb()
        if typ == "P_TAN_PUSH":
            return self._push_cb()
        raise TanError(f"Unknown TAN type {typ}")

    def _secondary_token(self, primary_token):
        r = requests.post(
            self.TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "cd_secondary",
                "token": primary_token,
            },
        )
        if r.status_code != 200:
            raise AuthenticationError("Secondary OAuth failed")
        return r.json()
