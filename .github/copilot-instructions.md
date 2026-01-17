# Comdirect API Python Client Instructions

## Project Overview
This project is a Python wrapper for the Comdirect Bank REST API. It handles authentication (OAuth + 2FA) and provides methods to access account balances, depots, and documents.

## Architecture & Core Components

### Client (`src/comdirect_api/client.py`)
- **Central Class**: `ComdirectClient` is the main entry point.
- **Initialization**: Takes `credentials` (dict) and `tan_handlers` (dict) as arguments.
- **Methods**: Provides high-level methods like `list_account_balances()`, `list_transactions()`, `list_depots()`.

### Authentication (`src/comdirect_api/auth.py`)
- **Class**: `Authenticator` handles the OAuth flow.
- **Flow**:
  1. Requests primary token (password grant).
  2. Handles 2FA challenge (PhotoTAN, SMS-TAN, PushTAN) using provided callbacks.
  3. Obtains secondary token and session ID.

### Session Management (`src/comdirect_api/session_manager.py`)
- **Class**: `ComdirectSession` wraps `requests.Session`.
- **Headers**: Automatically adds required headers (`Authorization`, `x-http-request-info`) to every request.

### Data Models (`src/comdirect_api/models/`)
- Response data is parsed into Pydantic-style or standard Python classes.
- Examples: `AccountBalance`, `AccountTransaction`, `Depot`, `DepotPosition`.

## Development Workflow

### Setup & Credentials
- **Credentials**: Store credentials in a `.env` file in the root directory (see `.env_EXAMPLE`).
  - Variables: `COMDIRECT_USERNAME`, `COMDIRECT_PASSWORD`, `COMDIRECT_CLIENT_ID`, `COMDIRECT_CLIENT_SECRET`.
- **Examples**: Runnable scripts are in `examples/` (e.g., `examples/basic_example.py`).

### Testing & Linting
- **Test Runner**: Uses `tox` if configured, or standard `pytest` (though tests are currently sparse/missing due to API restrictions).
- **Style**: Follow PEP 8.

### Packaging
- Uses `pyproject.toml`.
- Install editable: `pip install -e .`

## Coding Conventions

### Adding New Features
1. **Identifier API Endpoint**: Check `http.py` or existing methods in `client.py` to see how requests are made.
2. **Create/Update Model**: Add a new class in `src/comdirect_api/models/` if the response structure is new.
3. **Add Method to Client**: expose the functionality via `ComdirectClient`.

### Error Handling
- `AuthenticationError`: For login failures.
- Import from `comdirect_api.exceptions`.

## Key Files
- `src/comdirect_api/client.py`: High-level API.
- `src/comdirect_api/auth.py`: Low-level Auth logic.
- `examples/basic_example.py`: Reference implementation for consumers.
