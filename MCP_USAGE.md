# Comdirect API MCP Server

This MCP server exposes your Comdirect accounts, transactions, depots, and documents to MCP-compliant clients (like Claude Desktop or other AI agents).

## Prerequisites

- Python 3.12+
- `mcp` python package implementation
- Your `comdirect-api-wrapper` installation

## Installation

1.  Ensure you have the project installed (or are in the root with dependencies):
    ```bash
    uv pip install .  # Installs comdirect_api_wrapper
    uv pip install mcp
    ```
    *Note: The `mcp` package is required for the server implementation.*

## Configuration

The server requires your Comdirect credentials. It supports standard environment variables or a `.env` file.

### Environment Variables

Set the following variables:

- `COMDIRECT_CLIENT_ID`
- `COMDIRECT_CLIENT_SECRET`
- `COMDIRECT_USERNAME`
- `COMDIRECT_PASSWORD`

If these are not found in the environment, the server will attempt to load them from a `.env` file in the working directory.

## Usage with Claude Desktop

Add the server to your `claude_desktop_config.json` (usually in `~/Library/Application Support/Claude/` on macOS or `%APPDATA%\Claude\` on Windows).

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

*Note: Make sure to use the absolute path to your python executable if you are using a virtual environment (e.g. `/home/user/comdirect-api-wrapper/.venv/bin/python`).*

## Usage with VS Code Copilot

This project includes a pre-configured `.vscode/mcp.json` for immediate use with GitHub Copilot.

1.  Open `.vscode/mcp.json`.
2.  Updates the credentials or ensure they are set in your local `.env` file.
3.  The tool should be automatically detected by Copilot.

## Example Agent

An example agent definition is provided in `.github/agents/ComdirectAgent.agent.md`. This agent is configured with a specific persona (cynical, "r/mauerstrassenwetten" style) to demonstrate how to prompt the MCP tools effectively.

You can use this as a template for creating your own custom agents.

## Available Tools

- `login`: Establish session (triggers 2FA flow if required, outputting instructions to stderr).
- `list_accounts`: List all checking/savings accounts.
- `list_transactions`: List transactions for a specific account.
    - Args: `account_id`, `transaction_state` (default="BOOKED"), `min_booking_date`, `max_booking_date`.
- `list_depots`: List securities accounts.
- `get_depot_positions`: Get current portfolio positions for a depot.
- `list_documents`: List Postbox documents.
- `download_document`: Download a PDF document (returned as base64 encoded string).
    - Args: `document_id`, `mime_type`.

## Security Note

This server runs locally and accesses your real bank account.
- **Never share your credentials.**
- **Review MCP configuration carefully.**
- The server performs read-only operations mostly, but `login` triggers 2FA which sends push notifications/SMS.
