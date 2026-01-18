import json
from openapi_client import ApiClient, Configuration
from openapi_client.api.banking_api import BankingApi
from openapi_client.api.brokerage_api import BrokerageApi
from openapi_client.api.messages_api import MessagesApi
from openapi_client.exceptions import ApiException

from .auth import Authenticator
from .utils import timestamp
from .domain.models import (
    Account,
    Transaction,
    Depot,
    DepotPosition,
    DepotBalance,
    Document,
)
from .domain.mappers import (
    map_account,
    map_transaction,
    map_depot,
    map_depot_position,
    map_depot_balance,
    map_document,
)


class ComdirectApiClient(ApiClient):
    """
    Subclass of generated ApiClient to inject the dynamic x-http-request-info header.
    """

    def __init__(self, session_id_provider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session_id_provider = session_id_provider

    def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ):
        if header_params is None:
            header_params = {}

        # 1. Inject Authorization header if access_token is configured
        if self.configuration.access_token and "Authorization" not in header_params:
            header_params["Authorization"] = f"Bearer {self.configuration.access_token}"

        # 2. Inject x-http-request-info header if session exists
        session_id = self._session_id_provider()
        if session_id:
            request_info = {
                "clientRequestId": {
                    "sessionId": session_id,
                    "requestId": timestamp(),
                }
            }
            header_params["x-http-request-info"] = json.dumps(request_info)

        # 3. Ensure Content-Type is valid for Comdirect (sometimes they are picky)
        if "Content-Type" not in header_params:
            header_params["Content-Type"] = "application/json"

        return super().call_api(
            method,
            url,
            header_params=header_params,
            body=body,
            post_params=post_params,
            _request_timeout=_request_timeout,
        )


class ComdirectClient:
    def __init__(self, credentials, tan_handlers):
        self._auth = Authenticator(**credentials, **tan_handlers)
        self._session_id = None

        # Initialize OpenAPI client with default configuration
        config = Configuration(host="https://api.comdirect.de/api")
        # We use a lambda to provide the current session_id dynamically to the ApiClient
        self._api_client = ComdirectApiClient(session_id_provider=lambda: self._session_id, configuration=config)

        # Instantiate generated API classes once
        self._banking = BankingApi(self._api_client)
        self._brokerage = BrokerageApi(self._api_client)
        self._messages = MessagesApi(self._api_client)

    def login(self):
        # 1. Authenticate (keep existing flow)
        session_id, auth_result = self._auth.authenticate()

        # 2. Store session and token
        self._session_id = session_id
        access_token = auth_result["access_token"]

        # 3. Inject the token into the existing API client configuration
        self._api_client.configuration.access_token = access_token

    def list_accounts(self) -> list[Account]:
        """
        Returns a list of domain Account objects.
        """
        try:
            res = self._banking.banking_v2_get_account_balances(user="user")
            return [map_account(b) for b in res.values]
        except ApiException as e:
            raise e

    # def get_account_balance(self, account_id):
    #     # Not exposed to avoid leaking generated models.
    #     pass

    def list_transactions(self, account_id: str) -> list[Transaction]:
        """
        Returns a list of domain Transaction objects.
        """
        try:
            res = self._banking.banking_v1_get_account_transactions(account_id)
            return [map_transaction(tx, account_id) for tx in res.values]
        except ApiException as e:
            raise e

    def iter_all_transactions(self, account_id: str):
        """
        Iterates over all transactions for an account, handling pagination automatically.
        Note: Only returns 'BOOKED' transactions as the API only supports paging for those.
        """
        offset = 0
        while True:
            res = self._banking.banking_v1_get_account_transactions(
                account_id,
                paging_first=offset,
                transaction_state="BOOKED",
            )
            if not res.values:
                break
            yield from [map_transaction(tx, account_id) for tx in res.values]
            offset += len(res.values)

    def list_depots(self) -> list[Depot]:
        """
        Returns a list of Depot objects.
        """
        try:
            res = self._brokerage.brokerage_v3_get_depots(user_id="user")
            return [map_depot(d) for d in res.values]
        except ApiException as e:
            raise e

    def get_depot_positions(self, depot_id: str) -> tuple[DepotBalance, list[DepotPosition]]:
        """
        Returns (DepotBalance, List[DepotPosition]).
        """
        try:
            res = self._brokerage.brokerage_v3_get_depot_positions(depot_id)
            balance = map_depot_balance(res.aggregated)
            positions = [map_depot_position(p) for p in res.values]
            return balance, positions
        except ApiException as e:
            raise e

    def list_documents(self, paging_first=0, paging_count=1000) -> list[Document]:
        """
        Returns a list of Document objects.
        """
        try:
            # Map parameters
            kwargs = {
                "paging_first": paging_first,
                "paging_count": paging_count,
            }
            res = self._messages.messages_v2_get_documents(user="user", **kwargs)
            return [map_document(d) for d in res.values]
        except ApiException as e:
            raise e

    def download_document(self, document_id: str, mime_type: str) -> bytes:
        """
        Downloads a document.
        """
        try:
            # Pass Accept header via _headers argument
            response = self._messages.messages_v2_get_document(document_id, _headers={"Accept": mime_type})
            # Response is ApiResponse because type mapping is empty/None in generated code for this endpoint
            return response.raw_data
        except ApiException as e:
            raise e

    def logout(self):
        # We just clear local state.
        self._session_id = None
        self._api_client.configuration.access_token = None
