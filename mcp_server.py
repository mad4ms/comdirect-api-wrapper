import sys
import os
import json
import dataclasses
import asyncio
import time
import base64
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print(
        "Error: The 'mcp' package is required. Install with 'pip install mcp'.",
        file=sys.stderr,
    )
    sys.exit(1)

from comdirect_api.client import ComdirectClient

server = Server("comdirect-mcp")

# --------- Client Lifecycle / State ---------

_client: Optional[ComdirectClient] = None  # Singleton client instance


def _build_client() -> ComdirectClient:
    """
    Builds the ComdirectClient from environment variables.
    Credentials should be kept strictly on the server side.
    """
    required_creds = ["client_id", "client_secret", "username", "password"]
    credentials = {}

    # Try simple environment variables first
    for key in required_creds:
        env_key = f"COMDIRECT_{key.upper()}"
        if env_key in os.environ:
            credentials[key] = os.environ[env_key]

    # If missing credentials, try loading .env (fallback)
    if not all(k in credentials for k in required_creds):
        load_dotenv()
        for key in required_creds:
            env_key = f"COMDIRECT_{key.upper()}"
            if env_key in os.environ and key not in credentials:
                credentials[key] = os.environ[env_key]

    # Minimal default TAN handlers for headless MCP environment
    def _default_push_tan():
        sys.stderr.write("Push TAN requested. Please approve on your mobile device within 10 seconds.\n")
        time.sleep(10)
        return ""

    def _default_photo_tan(png_bytes):
        raise NotImplementedError("PhotoTAN is not supported in headless MCP mode.")

    def _default_sms_tan():
        raise NotImplementedError("SMS TAN is not supported in headless MCP mode.")

    tan_handlers = {
        "push_tan_cb": _default_push_tan,
        "photo_tan_cb": _default_photo_tan,
        "sms_tan_cb": _default_sms_tan,
    }

    return ComdirectClient(credentials=credentials, tan_handlers=tan_handlers)


def _get_client() -> ComdirectClient:
    """Gets or initializes the authenticated client."""
    global _client
    if _client is None:
        _client = _build_client()
        _client.login()
    return _client


def _jsonable(obj: Any) -> Any:
    """Serializer for domain models to JSON-compatible types."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if hasattr(obj, "model_dump"):  # pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):  # pydantic v1
        return obj.dict()
    # Fallback to dict if available
    return getattr(obj, "__dict__", str(obj))


def _ok(payload: Any) -> List[TextContent]:
    """Wraps success response in MCP TextContent."""
    return [
        TextContent(
            type="text",
            text=json.dumps(payload, ensure_ascii=False, default=_jsonable),
        )
    ]


def _err(msg: str) -> List[TextContent]:
    """Wraps error response."""
    return [TextContent(type="text", text=f"Error: {msg}")]


# --------- Tools Definition ---------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="login",
            description="Forces login/token refresh for the Comdirect session.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="logout",
            description="Logs out the current session.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_accounts",
            description="Lists all accounts (checking, savings, etc.).",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_transactions",
            description="Lists transactions for a specific account. Supports filtering by date and state.",
            inputSchema=ListTransactionsArgs.model_json_schema(),
        ),
        Tool(
            name="list_depots",
            description="Lists all securities accounts (Depots).",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_depot_positions",
            description="Gets positions (stocks, ETFs) and balance for a specific depot.",
            inputSchema=GetDepotPositionsArgs.model_json_schema(),
        ),
        Tool(
            name="list_documents",
            description="Lists available documents (Postbox).",
            inputSchema=ListDocumentsArgs.model_json_schema(),
        ),
        Tool(
            name="download_document",
            description="Downloads a specific document by ID. Returns base64 encoded content.",
            inputSchema=DownloadDocumentArgs.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        # Dispatcher
        if name == "login":
            return await login()
        elif name == "logout":
            return await logout()
        elif name == "list_accounts":
            return await list_accounts()
        elif name == "list_transactions":
            return await list_transactions(ListTransactionsArgs(**arguments))
        elif name == "list_depots":
            return await list_depots()
        elif name == "get_depot_positions":
            return await get_depot_positions(GetDepotPositionsArgs(**arguments))
        elif name == "list_documents":
            return await list_documents(ListDocumentsArgs(**arguments))
        elif name == "download_document":
            return await download_document(DownloadDocumentArgs(**arguments))
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        # Catch-all for API or Client errors
        return _err(f"Tool execution failed: {type(e).__name__}: {e}")


# --------- Implementation Handlers ---------


async def login():
    global _client
    _client = _build_client()
    _client.login()
    return _ok({"status": "logged_in"})


async def logout():
    global _client
    if _client:
        _client.logout()
    _client = None
    return _ok({"status": "logged_out"})


async def list_accounts():
    c = _get_client()
    accounts = c.list_accounts()
    return _ok({"accounts": accounts})


class ListTransactionsArgs(BaseModel):
    account_id: str = Field(..., description="Comdirect accountId")
    transaction_state: Optional[Literal["BOOKED", "NOTBOOKED"]] = Field(
        default="BOOKED",
        description="Comdirect transactionState. BOOKED supports paging; NOTBOOKED does not.",
    )
    transaction_direction: Optional[Literal["INCOMING", "OUTGOING"]] = None
    min_booking_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD (inclusive)",
    )
    max_booking_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD (inclusive)",
    )
    limit: int = Field(
        default=250,
        ge=1,
        le=2000,
        description="Hard limit to protect from huge outputs; server stops after this many items.",
    )


async def list_transactions(args: ListTransactionsArgs):
    c = _get_client()
    out = []

    # iter_all_transactions is a generator provided by the client wrapper
    iterator = c.iter_all_transactions(
        account_id=args.account_id,
        transaction_state=args.transaction_state,
        transaction_direction=args.transaction_direction,
        min_booking_date=args.min_booking_date,
        max_booking_date=args.max_booking_date,
    )

    for tx in iterator:
        out.append(tx)
        if len(out) >= args.limit:
            break

    return _ok(
        {
            "account_id": args.account_id,
            "count": len(out),
            "truncated": len(out) >= args.limit,
            "transactions": out,
        }
    )


async def list_depots():
    c = _get_client()
    depots = c.list_depots()
    return _ok({"depots": depots})


class GetDepotPositionsArgs(BaseModel):
    depot_id: str


async def get_depot_positions(args: GetDepotPositionsArgs):
    c = _get_client()
    balance, positions = c.get_depot_positions(args.depot_id)
    return _ok({"depot_id": args.depot_id, "balance": balance, "positions": positions})


class ListDocumentsArgs(BaseModel):
    paging_first: int = 0
    paging_count: int = Field(default=200, ge=1, le=1000)


async def list_documents(args: ListDocumentsArgs):
    c = _get_client()
    docs = c.list_documents(paging_first=args.paging_first, paging_count=args.paging_count)

    # Transform domain models to simple dicts
    # Using direct attribute access as expected from domain.models.Document
    slim_docs = [
        {
            "document_id": d.id,
            "name": d.name,
            "date": d.date_creation,
            "mime_type": d.mime_type,
            "advertisement": d.advertisement,
        }
        for d in docs
    ]

    return _ok({"count": len(slim_docs), "documents": slim_docs})


class DownloadDocumentArgs(BaseModel):
    document_id: str
    mime_type: str = Field(..., description="e.g. application/pdf")


async def download_document(args: DownloadDocumentArgs):
    c = _get_client()
    raw_bytes = c.download_document(args.document_id, args.mime_type)
    b64_str = base64.b64encode(raw_bytes).decode("ascii")

    return _ok(
        {
            "document_id": args.document_id,
            "mime_type": args.mime_type,
            "base64": b64_str,
        }
    )


# --------- Entrypoint ---------


async def main():
    # stdio_server handles the JSON-RPC communication over stdin/stdout
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
