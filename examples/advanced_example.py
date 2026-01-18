import os
import sys
from collections import defaultdict
from decimal import Decimal
from dotenv import load_dotenv

# Add src to path so we can import comdirect_api simply by running this script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))  # noqa

from comdirect_api.client import ComdirectClient  # noqa
from comdirect_api.utils import (  # noqa
    default_photo_tan_callback,
    default_sms_tan_callback,
    default_push_tan_callback,
)


def print_header(title):
    print(f"\n{'-'*60}")
    print(f"{title}")
    print(f"{'-'*60}")


def analyze_wealth(client: ComdirectClient):
    print_header("1. TOTAL WEALTH OVERVIEW")

    total_wealth = Decimal(0)

    # 1. Cash Accounts
    accounts = client.list_accounts()
    print(f"Checking {len(accounts)} cash accounts...")
    for acc in accounts:
        # Assuming EUR for simplicity in this example
        if acc.currency == "EUR":
            total_wealth += acc.balance
            print(f" - Account {acc.id}: {acc.balance:,.2f} EUR")

    # 2. Depot Values
    depots = client.list_depots()
    print(f"Checking {len(depots)} depots...")
    for depot in depots:
        balance, _ = client.get_depot_positions(depot.id)
        if balance.current_value_currency == "EUR":
            total_wealth += balance.current_value
            print(f" - Depot {depot.id}: {balance.current_value:,.2f} EUR")

    print(f"\n>>> TOTAL CALCULATED WEALTH: {total_wealth:,.2f} EUR")


def analyze_cash_flow(client: ComdirectClient):
    print_header("2. CASH FLOW ANALYSIS (Last 90 Days)")

    accounts = client.list_accounts()
    if not accounts:
        print("No accounts found.")
        return

    # Use the first account for demo purposes
    main_account_id = accounts[0].id
    print(f"Analyzing main account: {main_account_id}")

    # Fetch last ~90 days of transactions (approx via listing)
    # We'll just grab everything available via the iterator helper
    # In a real app, you might stop iteration after a certain date

    income = Decimal(0)
    expenses = Decimal(0)
    monthly_stats = defaultdict(lambda: {"in": Decimal(0), "out": Decimal(0)})

    count = 0
    print("Fetching and processing transactions...")

    for tx in client.iter_all_transactions(main_account_id):
        # We only look at EUR
        if tx.currency != "EUR":
            continue

        count += 1
        year_month = tx.booking_date.strftime("%Y-%m")

        if tx.amount > 0:
            income += tx.amount
            monthly_stats[year_month]["in"] += tx.amount
        else:
            expenses += tx.amount
            monthly_stats[year_month]["out"] += tx.amount

    print(f"Processed {count} transactions.")
    print(f"Total Income:   {income:,.2f} EUR")
    print(f"Total Expenses: {expenses:,.2f} EUR")
    print(f"Net Cash Flow:  {(income + expenses):,.2f} EUR")

    print("\nMonthly Breakdown:")
    for ym in sorted(monthly_stats.keys()):
        stats = monthly_stats[ym]
        net = stats["in"] + stats["out"]
        print(f" - {ym}: In {stats['in']:>10.2f} | Out {stats['out']:>10.2f} | Net {net:>10.2f}")


def analyze_portfolio(client: ComdirectClient):
    print_header("3. PORTFOLIO PERFORMANCE")

    depots = client.list_depots()
    if not depots:
        print("No depots found.")
        return

    for depot in depots:
        balance, positions = client.get_depot_positions(depot.id)

        print(f"Depot {depot.id} ({depot.display_id})")
        print(f"Current Value: {balance.current_value:,.2f} {balance.current_value_currency}")

        if balance.purchase_value:
            abs_gain = balance.current_value - balance.purchase_value
            rel_gain = (abs_gain / balance.purchase_value) * 100
            print(f"Overall Gain:  {abs_gain:,.2f} EUR ({rel_gain:.2f}%)")

        print("\nTop 3 Performers (Relative Gain):")
        # Filter positions that have performance data
        valid_pos = [p for p in positions if p.profit_loss_purchase_rel is not None]

        # Sort by relative gain descending. API returns string like "12.5%", strip % and convert
        def get_rel_gain(p):
            try:
                return float(p.profit_loss_purchase_rel.replace("%", "").replace(",", "."))
            except (ValueError, AttributeError):
                return -999999.0

        sorted_pos = sorted(valid_pos, key=get_rel_gain, reverse=True)

        for p in sorted_pos[:3]:
            gain_raw = p.profit_loss_purchase_rel
            name = p.instrument_name or p.wkn
            val = p.current_value
            print(f" - {name[:30]:<30} | {gain_raw:>8} | Value: {val:>10.2f} EUR")


def main():
    load_dotenv()

    # Credentials check
    try:
        credentials = {
            "username": os.environ["COMDIRECT_USERNAME"],
            "password": os.environ["COMDIRECT_PASSWORD"],
            "client_id": os.environ["COMDIRECT_CLIENT_ID"],
            "client_secret": os.environ["COMDIRECT_CLIENT_SECRET"],
        }
    except KeyError:
        print("Please configure your .env file with COMDIRECT_ credentials.")
        return

    tan_handlers = {
        "photo_tan_cb": default_photo_tan_callback,
        "sms_tan_cb": default_sms_tan_callback,
        "push_tan_cb": default_push_tan_callback,
    }

    print("Initializing and logging in...")
    client = ComdirectClient(credentials, tan_handlers)

    try:
        client.login()
        print("Login successful.")

        # Run Analyses
        analyze_wealth(client)
        analyze_cash_flow(client)
        analyze_portfolio(client)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\nLogging out...")
        if client:
            client.logout()


if __name__ == "__main__":
    main()
