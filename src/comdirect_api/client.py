from .auth import Authenticator
from .http import ComdirectHttpClient
from .session_manager import ComdirectSession
from .models.account import AccountBalance, AccountTransaction
from .models.document import Document
from .models.depot import Depot, DepotPosition, DepotBalance

API_BASE = "https://api.comdirect.de/api"


class ComdirectClient:
    def __init__(self, credentials, tan_handlers):
        self._auth = Authenticator(**credentials, **tan_handlers)
        self._session = None
        self._http = None

    def login(self):
        session_id, auth_result = self._auth.authenticate()
        self._session = ComdirectSession(session_id, auth_result)
        self._http = ComdirectHttpClient(API_BASE, self._session)

    def list_account_balances(self, paging_first=0, paging_count=1000):
        params = {"paging-first": paging_first, "paging-count": paging_count}
        r = self._http.request(
            "GET",
            "/banking/clients/user/v1/accounts/balances",
            params=params,
        )
        return [AccountBalance.from_api(x) for x in r.json()["values"]]

    def get_account_balance(self, account_id):
        r = self._http.request("GET", f"/banking/v2/accounts/{account_id}/balances")
        return AccountBalance.from_api(r.json())

    def list_transactions(
        self,
        account_id,
        paging_first=0,
        paging_count=None,
        transaction_direction="CREDIT_AND_DEBIT",
        transaction_state="BOTH",
        min_booking_date=None,
        max_booking_date=None,
    ):
        params = {
            "paging-first": paging_first,
            "transactionDirection": transaction_direction,
            "transactionState": transaction_state,
        }
        if paging_count is not None:
            params["paging-count"] = paging_count
        if min_booking_date:
            params["min-bookingdate"] = min_booking_date
        if max_booking_date:
            params["max-bookingdate"] = max_booking_date

        r = self._http.request(
            "GET",
            f"/banking/v1/accounts/{account_id}/transactions",
            params=params,
        )
        return [AccountTransaction.from_api(x) for x in r.json()["values"]]

    def list_depots(self, paging_first=0, paging_count=1000):
        params = {"paging-first": paging_first, "paging-count": paging_count}
        r = self._http.request("GET", "/brokerage/clients/user/v3/depots", params=params)
        return [Depot.from_api(x) for x in r.json()["values"]]

    def get_depot_positions(self, depot_id):
        r = self._http.request("GET", f"/brokerage/v3/depots/{depot_id}/positions")
        data = r.json()
        balance = DepotBalance.from_api(data["aggregated"])
        positions = [DepotPosition.from_api(x) for x in data["values"]]
        return balance, positions

    def list_documents(self, paging_first=0, paging_count=1000):
        params = {"paging-first": paging_first, "paging-count": paging_count}
        r = self._http.request(
            "GET",
            "/messages/clients/user/v2/documents",
            params=params,
        )
        return [Document.from_api(x) for x in r.json()["values"]]

    def download_document(self, document_id, mime_type):
        r = self._http.request(
            "GET",
            f"/messages/v2/documents/{document_id}",
            headers={"Accept": mime_type},
        )
        return r.content

    def logout(self):
        if self._session:
            self._session.revoke()
