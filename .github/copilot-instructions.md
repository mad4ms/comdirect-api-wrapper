# Comdirect API Python Client Instructions

## Project Overview
This project is a modern Python wrapper for the Comdirect Bank REST API. It uses a **hybrid architecture**:
1.  **Generated Core**: A stable, auto-generated low-level client (`openapi_client`) based on the official Swagger specification.
2.  **Hand-Written Wrapper**: A high-level, pythonic layer (`comdirect_api`) that abstracts away authentication, session management, and type mapping.

## Architecture

### 1. The High-Level Client (`src/comdirect_api/`)
*   **`client.py`**:
    *   `ComdirectClient`: The main entry point. Orchestrates the 2FA flow and delegates calls to the generated API classes.
    *   `ComdirectApiClient`: A subclass of the generated `ApiClient`. It injects dynamic headers (`x-http-request-info`) and handles token renewal/injection automatically.
*   **`auth.py`**: Handles the complex OAuth-like flow (Password Grant -> Challenge (PhotoTAN/App) -> Session).
*   **`domain/models.py`**: Simple, frozen `dataclasses` that represent the *clean* API surface exposed to users. We do NOT expose generated Pydantic models directly to end users to maintain API stability.
*   **`domain/mappers.py`**: Functions to map raw `openapi_client` models to `domain.models`.

### 2. The Generated Core (`src/openapi_client/`)
*   Generated using `openapi-generator-cli` from `scripts/bootstrap_client.sh`.
*   Contains low-level Pydantic V2 models (`src/openapi_client/models/`) and request logic.
*   **DO NOT EDIT FILES IN THIS DIRECTORY MANUALLY** (except for temporary debugging). Changes will be overwritten.
*   Modifications to the API spec should happen in `scripts/patch_openapi.py`.

## Development Workflow

### Client Generation
The client is generated from the official Swagger JSON, which requires patching because the spec often mismatches the actual API behavior (e.g., date formats, string lengths, missing fields).
*   **Script**: `./scripts/bootstrap_client.sh`
*   **Patching**: `scripts/patch_openapi.py` (Edit this to fix validation errors like "String length > 50").
*   **Process**: Downloads spec -> Patches JSON -> Runs Generator -> Installs to `src/openapi_client`.
*   **Documentation**: See `GENERATION.md`.

### Setup & Credentials
*   **Environment**: Uses `uv` for dependency management.
*   **Credentials**: `.env` file (see `.env_EXAMPLE`).
    *   `COMDIRECT_USERNAME`, `COMDIRECT_PASSWORD`, `COMDIRECT_CLIENT_ID`, `COMDIRECT_CLIENT_SECRET`.

### Coding Standards
*   **Style**: PEP 8.
*   **Type Hinting**: Fully typed.
*   **Error Handling**: Wrap generated `ApiException` in high-level exceptions if possible, or let them bubble up if they are informative.

## Key Files
*   `src/comdirect_api/client.py`: Main logic binding everything together.
*   `src/comdirect_api/domain/models.py`: The user-facing public API surface.
*   `examples/basic_example.py`: The canonical reference for how to use the library.
*   `scripts/patch_openapi.py`: Critical for fixing API spec violations.

## Troubleshooting
*   **Validation Errors**: If the API returns data that violates restrictions (e.g., `maxLength`), do not relax the Pydantic model manually. Add a patch to `scripts/patch_openapi.py` and regenerate.
*   **Missing Fields**: If a field is missing in the response, check `tmp/comdirect_openapi.json` to see if it's defined.
