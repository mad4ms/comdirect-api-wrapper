import requests


class ComdirectSession:
    REVOKE_URL = "https://api.comdirect.de/oauth/revoke"

    def __init__(self, session_id: str, auth_result: dict):
        self.session_id = session_id
        self.access_token = auth_result["access_token"]
        self.refresh_token = auth_result["refresh_token"]
        self.kdnr = auth_result.get("kdnr")
        self.bpid = auth_result.get("bpid")
        self.kontakt_id = auth_result.get("kontaktId")
        self._revoked = False

    def token(self):
        return self.access_token

    def revoke(self):
        if self._revoked:
            return
        r = requests.delete(
            self.REVOKE_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        if r.status_code != 204:
            raise RuntimeError("Token revoke failed")
        self._revoked = True
