import os
import sys
from dotenv import load_dotenv

# Add src to path so we can import comdirect_api simply by running this script
# This allows running the example without installing the package
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))  # noqa

from comdirect_api.client import ComdirectClient  # noqa
from comdirect_api.utils import (  # noqa
    default_photo_tan_callback,
    default_sms_tan_callback,
    default_push_tan_callback,
)


def main():
    # Load environment variables from .env file
    # Ensure you have created a .env file based on .env_EXAMPLE
    load_dotenv()

    # Get credentials
    try:
        credentials = {
            "username": os.environ["COMDIRECT_USERNAME"],
            "password": os.environ["COMDIRECT_PASSWORD"],
            "client_id": os.environ["COMDIRECT_CLIENT_ID"],
            "client_secret": os.environ["COMDIRECT_CLIENT_SECRET"],
        }
    except KeyError as e:
        print(f"Error: Missing environment variable {e}")
        print("Please create a .env file in the root directory based on .env_EXAMPLE")
        return

    # Define callbacks for 2FA
    # You can use the defaults or provide authentication specific logic here
    tan_handlers = {
        "photo_tan_cb": default_photo_tan_callback,
        "sms_tan_cb": default_sms_tan_callback,
        "push_tan_cb": default_push_tan_callback,
    }

    # Initialize client
    print("Initializing client ...")
    client = ComdirectClient(credentials, tan_handlers)

    print("Logging in ...")
    try:
        client.login()
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    try:
        # Fetch account balances
        print("\nFetching Account Balances:")
        balances = client.list_account_balances()
        for balance in balances:
            print(f"- Account: {balance.account_id}")
            print(f"  Balance: {balance.balance.value} {balance.balance.currency}")
            print(f"  Available: {balance.balance_eur.value} {balance.balance_eur.currency}")

        # If there are accounts, fetch transactions for the first one
        if balances:
            first_account_id = balances[0].account_id
            print(f"\nFetching transactions for Account {first_account_id}:")
            transactions = client.list_transactions(first_account_id)
            if not transactions:
                print("No transactions found.")
            for tx in transactions[:5]:  # Show first 5
                print(f"- {tx.booking_date}: {tx.amount.value} {tx.amount.currency} ({tx.transaction_type.name})")

        # Fetch Depots
        print("\nFetching Depots:")
        depots = client.list_depots()
        for depot in depots:
            print(f"- Depot ID: {depot.depot_id}, Holder: {depot.holder_name}")

            # Fetch positions
            print(f"  Fetching positions for depot {depot.depot_id}...")
            balance, positions = client.get_depot_positions(depot.depot_id)
            print(f"  Depot Value: {balance.current_value} EUR")
            for pos in positions[:5]:
                print(f"  - WKN: {pos.wkn}, Quantity: {pos.quantity}, Value: {pos.current_value}")

    except Exception as e:
        print(f"An error occurred during data fetching: {e}")

    finally:
        print("\nLogging out...")
        client.logout()
        print("Logged out.")


if __name__ == "__main__":
    main()
