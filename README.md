# comdirect-api-wrapper
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
<p align="left">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Comdirect_Logo_2017.png" alt="Comdirect Logo" width="200px">
</p>

This is a Python implementation of the new [comdirect REST API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html). This API can be used to interact with the German bank comdirect and view your balances, transactions, and depot. The technical specification of the API (in German) is found [here](https://kunde.comdirect.de/cms/media/comdirect_REST_API_Dokumentation.pdf).

## Features

Parts which are implemented and working:
- OAuth 2-factor login process (Photo-TAN, Push-TAN, SMS-TAN)
- ACCOUNT (balances & transactions)
- DEPOT (positions & balances)
- DOCUMENTS

## Installation

This Python module is currently not on PyPI.

### Using uv (Recommended)

To add this project to your `uv` managed project:

```bash
uv add git+https://github.com/mad4ms/comdirect-api-wrapper.git
```

### Local Development

To install dependencies and set up the environment for development:

```bash
git clone https://github.com/mad4ms/comdirect-api-wrapper.git
cd comdirect-api-wrapper
uv sync
```

## Usage

See `examples/basic_example.py` for a complete example of how to authenticate and fetch data.

### Configuration

You need to provide your credentials. The example script uses a `.env` file (you can copy `.env_EXAMPLE` to `.env`).

```bash
cp .env_EXAMPLE .env
# Edit .env and add your USERNAME, PASSWORD, CLIENT_ID, and CLIENT_SECRET
```

⚠️⚠️⚠️ **Warning**: Make sure to keep your credentials secure and do not share them publicly. With great power comes great responsibility! ⚠️⚠️⚠️

### Running the Example

You can run the example script using `uv run`:

```bash
uv run examples/basic_example.py
```

### Basic Code Example

```python
from comdirect_api.client import ComdirectClient
from comdirect_api.utils import default_photo_tan_callback, default_sms_tan_callback, default_push_tan_callback

# Creds dictionary
credentials = {
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
}

# 2FA Callbacks
tan_handlers = {
    "photo_tan_cb": default_photo_tan_callback,
    "sms_tan_cb": default_sms_tan_callback,
    "push_tan_cb": default_push_tan_callback,
}

# Initialize and Login
client = ComdirectClient(credentials, tan_handlers)
client.login()

# Usage
# 1. Fetch Accounts
accounts = client.list_accounts()
for account in accounts:
    print(f"Account: {account.id}, Balance: {account.balance} {account.currency}")

# 2. Fetch Transactions (using iterator helper)
if accounts:
    print(f"Transactions for {accounts[0].id}:")
    for tx in client.iter_all_transactions(accounts[0].id):
        print(f" - {tx.booking_date}: {tx.amount} {tx.currency} | {tx.purpose}")

# 3. Fetch Depots & Positions
depots = client.list_depots()
for depot in depots:
    print(f"Depot: {depot.id}")
    balance, positions = client.get_depot_positions(depot.id)
    print(f"Value: {balance.current_value} {balance.current_value_currency}")
    for pos in positions:
        print(f" - {pos.quantity}x {pos.wkn}: {pos.current_value} {pos.current_value_currency}")

client.logout()
```

## Usage Policy

- **Public API**: Application code must only import `ComdirectClient` from `comdirect_api`.
- **Internal Implementation**: OpenAPI-generated code (`openapi_client`) is an internal implementation detail and should not be imported or used directly. But i can't really force you to not do it.
- **Data Models**: Use only the domain models provided by `comdirect_api.domain.models`. Generated OpenAPI models are not part of the public API.

## Development

- This project uses `uv` for dependency management.
- Source code is in `src/`.
- **OpenAPI Generation**: See [openapi/GENERATION.md](openapi/GENERATION.md) for instructions on updating the generated client code.
- Run examples with `uv run examples/basic_example.py`.
- Run tests (when available) with `uv run pytest`.
