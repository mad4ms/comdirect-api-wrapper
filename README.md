# comdirect-api-wrapper
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

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
balances = client.list_account_balances()
print(balances)

client.logout()
```

## Development

- This project uses `uv` for dependency management.
- Source code is in `src/`.
- Run examples with `uv run examples/basic_example.py`.
- Run tests (when available) with `uv run pytest`.
