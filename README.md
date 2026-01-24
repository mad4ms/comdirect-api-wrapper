# comdirect-api-wrapper

[![PyPI version](https://badge.fury.io/py/comdirect-api-wrapper.svg)](https://badge.fury.io/py/comdirect-api-wrapper)
[![Build Status](https://github.com/mad4ms/comdirect-api-wrapper/actions/workflows/publish.yml/badge.svg)](https://github.com/mad4ms/comdirect-api-wrapper/actions/workflows/publish.yml)
[![Tests](https://github.com/mad4ms/comdirect-api-wrapper/actions/workflows/tests.yml/badge.svg)](https://github.com/mad4ms/comdirect-api-wrapper/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat&logo=python)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A modern, type-safe Python wrapper for the [comdirect REST API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html).

This library allows you to interact with your Comdirect bank accounts programmatically. It handles the complex OAuth2 authentication flow (including 2FA challenge-response for PhotoTAN, PushTAN, and SMS-TAN), auto-refreshes tokens, and provides a pythonic interface for retrieving balances, transactions, and depot positions.

## Features

-   **Authentication**: Full OAuth2 support with automatic token refresh and session handling.
-   **2FA Support**: Built-in callbacks for PhotoTAN (App), PushTAN, and SMS-TAN.
-   **Banking**: Retrieve account lists, balances, and transaction history.
-   **Brokerage**: Fetch depot overviews and detailed position data.
-   **Documents**: Download postbox documents (PDFs).
-   **Type Safe**: Fully typed domain models for great IDE support and autocompletion.

## Installation

### Using uv (Recommended)

```bash
uv add comdirect-api-wrapper
```

### Using pip

```bash
pip install comdirect-api-wrapper
```

## Quick Start

### 1. Prerequisites

You need user credentials AND API credentials from Comdirect.
1.  Enable API access in your Comdirect settings (https://www.comdirect.de/cms/kontakt-zugaenge-api.html).
2.  Obtain your `client_id` and `client_secret`.
3. Your smartphone with the Comdirect PhotoTAN app installed (for 2FA).

### 2. Configuration

`python-dotenv` to manage secrets. Create a `.env` file:

```ini
COMDIRECT_USERNAME=your_username
COMDIRECT_PASSWORD=your_password
COMDIRECT_CLIENT_ID=your_client_id
COMDIRECT_CLIENT_SECRET=your_client_secret
```

### 3. Usage Example

```python
import os
from dotenv import load_dotenv
from comdirect_api.client import ComdirectClient
from comdirect_api.utils import default_photo_tan_callback, default_push_tan_callback

load_dotenv()

# 1. Setup Credentials
credentials = {
    "username": os.getenv("COMDIRECT_USERNAME"),
    "password": os.getenv("COMDIRECT_PASSWORD"),
    "client_id": os.getenv("COMDIRECT_CLIENT_ID"),
    "client_secret": os.getenv("COMDIRECT_CLIENT_SECRET"),
}

# 2. Setup 2FA Handlers (What happens when the bank asks for a TAN?)
tan_handlers = {
    # For PhotoTAN App (Push):
    "push_tan_cb": default_push_tan_callback,
    # For PhotoTAN Graphic (Scan):
    "photo_tan_cb": default_photo_tan_callback,
}

# 3. Initialize & Login
client = ComdirectClient(credentials, tan_handlers)
client.login() # Triggers 2FA interaction if needed

# 4. Fetch Data
# --- Accounts ---
for account in client.list_accounts():
    print(f"Account: {account.id} | Balance: {account.balance} {account.currency}")

    # Fetch Transactions
    for tx in client.list_transactions(account.id):
        print(f"  {tx.booking_date}: {tx.amount} {tx.currency} - {tx.purpose}")

    # # or
    # transactions = list(client.iter_all_transactions(account.id))
    # for tx in transactions:
    #     print(f"  {tx.booking_date}: {tx.amount} {tx.currency} - {tx.purpose}")

# --- Depot ---
for depot in client.list_depots():
    balance, positions = client.get_depot_positions(depot.id)
    print(f"Depot Value: {balance.current_value} EUR")
    for pos in positions:
        print(f"  {pos.quantity}x {pos.instrument_name} ({pos.wkn})")
```

## Advanced Usage

### Pagination

For accounts with many transactions, use the iterator which handles pagination automatically:

```python
for tx in client.iter_all_transactions(account_id):
    # This automatically fetches pages as you iterate
    process_transaction(tx)
```

### Document Retrieval

```python
docs = client.list_documents()
for doc in docs:
    print(f"Downloading {doc.name}...")
    pdf_bytes = client.download_document(doc.id, doc.mime_type)
    with open(f"{doc.name}.pdf", "wb") as f:
        f.write(pdf_bytes)
```

## Model Context Protocol (MCP) Server

This library includes a fully functional [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server. This allows AI assistants (like Claude Desktop) to connect directly to your Comdirect accounts to fetch balances, search transactions, and analyze your portfolio.

See [MCP_USAGE.md](MCP_USAGE.md) for setup and usage instructions.

### Quick Config for Claude Desktop

```json
{
  "mcpServers": {
    "comdirect": {
      "command": "python",
      "args": ["/absolute/path/to/comdirect-api-wrapper/mcp_server.py"],
      "env": {
        "COMDIRECT_CLIENT_ID": "...",
        "COMDIRECT_CLIENT_SECRET": "...",
        "COMDIRECT_USERNAME": "...",
        "COMDIRECT_PASSWORD": "..."
      }
    }
  }
}
```

## Disclaimer

This project is not affiliated with, maintained, or endorsed by the comdirect bank. Use this software at your own risk. I provide no warranty and accept no liability for any financial losses or damages resulting from the use of this software.

This project is designed to run locally and does not collect, store, or transmit your banking credentials to any third parties.

Nevertheless, be cautious and **review the code before use, especially when dealing with sensitive financial data**.

---

**License**: MIT

## Development

### Pre-commit Hooks

This project uses `pre-commit` to ensure code quality and prevent accidental secret commits.

1.  Install pre-commit:
    ```bash
    uv pip install pre-commit
    ```
2.  Install the git hooks:
    ```bash
    pre-commit install
    ```

Now, checks (formatting, linting, secret scanning) will run automatically before every commit.
