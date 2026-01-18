import base64
import json
import logging
import uuid
from typing import Any, Callable, Dict, Tuple

import requests

from .exceptions import AuthenticationError, TanError
from .utils import timestamp

logger = logging.getLogger(__name__)


class Authenticator:
    """
    Handles the complicated OAuth + 2FA authentication flow for Comdirect.
    """

    TOKEN_URL = "https://api.comdirect.de/oauth/token"
    SESSION_URL = "https://api.comdirect.de/api/session/clients/user/v1/sessions"

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        *,
        photo_tan_cb: Callable[[bytes], str],
        sms_tan_cb: Callable[[], str],
        push_tan_cb: Callable[[], str],
    ):
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._photo_cb = photo_tan_cb
        self._sms_cb = sms_tan_cb
        self._push_cb = push_tan_cb

        self._session = requests.Session()

    def authenticate(self) -> Tuple[str, Dict[str, Any]]:
        """
        Performs the full authentication flow.

        Returns:
            Tuple containing (session_id, token_response_dict)
        """
        logger.info("Starting authentication flow")
        try:
            token = self._primary_token()
            session_id = self._create_session(token)
            self._validate_session(token, session_id)
            secondary_token = self._secondary_token(token)

            logger.info("Authentication successful")
            return session_id, secondary_token

        except requests.RequestException as e:
            logger.error(f"Network error during authentication: {e}")
            raise AuthenticationError(f"Network error: {str(e)}") from e

    def _primary_token(self) -> str:
        """Step 1: Get initial OAuth access token using password grant."""
        logger.debug("Requesting primary token")
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "username": self._username,
            "password": self._password,
            "grant_type": "password",
        }

        response = self._session.post(
            self.TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=payload,
        )

        self._handle_error(response, "Primary OAuth failed")
        return response.json()["access_token"]

    def _create_session(self, token: str) -> str:
        """Step 2: Initialize a session with the API."""
        logger.debug("Creating API session")
        headers = self._get_base_headers(token)
        headers["x-http-request-info"] = self._build_request_info_header(str(uuid.uuid4()))

        response = self._session.get(self.SESSION_URL, headers=headers)

        self._handle_error(response, "Session creation creation failed")

        try:
            return response.json()[0]["identifier"]
        except (IndexError, KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid session response format: {response.text}") from e

    def _validate_session(self, token: str, session_id: str) -> None:
        """Step 3: Trigger 2FA challenge and validate session."""
        logger.debug("Validating session (2FA challenge)")

        request_info_header = self._build_request_info_header(session_id)
        headers = self._get_base_headers(token)
        headers.update(
            {
                "Content-Type": "application/json",
                "x-http-request-info": request_info_header,
            }
        )

        # Trigger 2FA
        response = self._session.post(
            f"{self.SESSION_URL}/{session_id}/validate",
            headers=headers,
            json={
                "identifier": session_id,
                "sessionTanActive": True,
                "activated2FA": True,
            },
        )
        self._handle_error(response, "Session validation init failed", expected_codes=[201])

        # Handle 2FA Challenge
        challenge_header = response.headers.get("x-once-authentication-info")
        if not challenge_header:
            raise AuthenticationError("Missing x-once-authentication-info header in response")

        auth_info = json.loads(challenge_header)
        logger.info("Received 2FA challenge of type: %s", auth_info.get("typ"))

        tan = self._resolve_tan(auth_info)

        # Confirm 2FA
        logger.debug("Submitting TAN")
        headers["x-once-authentication-info"] = json.dumps({"id": auth_info["id"]})
        headers["x-once-authentication"] = tan

        response2 = self._session.patch(
            f"{self.SESSION_URL}/{session_id}",
            headers=headers,
            json={
                "identifier": session_id,
                "sessionTanActive": True,
                "activated2FA": True,
            },
        )
        self._handle_error(response2, "TAN confirmation failed")

    def _secondary_token(self, primary_token: str) -> Dict[str, Any]:
        """Step 4: public token exchange for full access."""
        logger.debug("Requesting secondary token")
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "cd_secondary",
            "token": primary_token,
        }

        response = self._session.post(
            self.TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=payload,
        )
        self._handle_error(response, "Secondary OAuth failed")
        return response.json()

    def _resolve_tan(self, info: Dict[str, Any]) -> str:
        """Dispatches the TAN challenge to the correct callback."""
        typ = info.get("typ")

        try:
            if typ == "P_TAN":  # PhotoTAN
                challenge_raw = base64.b64decode(info["challenge"])
                return self._photo_cb(challenge_raw)
            elif typ == "M_TAN":  # SMS TAN
                return self._sms_cb()
            elif typ == "P_TAN_PUSH":  # App Approval
                return self._push_cb()
            else:
                raise TanError(f"Unknown TAN type: {typ}")
        except Exception as e:
            logger.error(f"Error in TAN callback: {e}")
            raise TanError(f"TAN callback failed: {str(e)}") from e

    def _handle_error(
        self,
        response: requests.Response,
        msg: str,
        expected_codes: list[int] = None,
    ):
        if expected_codes is None:
            expected_codes = [200]

        if response.status_code not in expected_codes:
            error_details = response.text
            try:
                # Try to parse nice error JSON if available
                details_json = response.json()
                if "error_description" in details_json:
                    error_details = details_json["error_description"]
                elif "error" in details_json:
                    error_details = details_json.get("error")
            except ValueError:
                pass

            logger.error(f"{msg}: HTTP {response.status_code} - {error_details}")
            raise AuthenticationError(f"{msg} (HTTP {response.status_code}): {error_details}")

    @staticmethod
    def _get_base_headers(token: str) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    def _build_request_info_header(session_id: str) -> str:
        return json.dumps(
            {
                "clientRequestId": {
                    "sessionId": session_id,
                    "requestId": timestamp(),
                }
            }
        )
