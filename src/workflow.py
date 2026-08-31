# src/workflow.py
import logging
from datetime import datetime, timedelta, timezone
from parser import parse_email

from gmail_agent import fetch_payment_emails, get_gmail_service
from sheets_agent import append_transactions_to_month_sheet, get_sheets_service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def update_sync_metadata(spreadsheet, latest_timestamp):
    """Update the metadata sheet with the latest sync timestamp."""
    try:
        metadata_sheet = spreadsheet.worksheet("_Metadata")
    except Exception:  # noqa: BLE001
        # Create metadata sheet if it doesn't exist
        metadata_sheet = spreadsheet.add_worksheet(title="_Metadata", rows=10, cols=2)
        metadata_sheet.append_row(["Last Sync Timestamp", "Last Sync Date"])

    # Update the timestamp in row 2
    metadata_sheet.update_cell(2, 1, latest_timestamp)

    # Also store a human-readable date
    readable_date = datetime.fromtimestamp(latest_timestamp, tz=timezone.utc).strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    metadata_sheet.update_cell(2, 2, readable_date)

    logger.info(f"Updated sync metadata to timestamp: {latest_timestamp}")


def get_month_name(date_str):
    """Convert date string (dd-mm-yyyy) to month name (e.g., 'August 2026')."""
    date_obj = datetime.strptime(date_str, "%d-%m-%Y").replace(tzinfo=timezone.utc)
    return date_obj.strftime("%B %Y")


def run_workflow():
    # Get sheet ID from environment variable
    sheet_id = "1HpfqX5ds6xCc5dWTcgRFeFwVU8HFgDRQSrgda35V1Hs"
    if not sheet_id:
        raise ValueError(
            "GOOGLE_SHEET_ID environment variable not set. "
            "Please set it to your Google Sheet ID."
        )

    gmail = get_gmail_service()
    sheets_client = get_sheets_service()
    spreadsheet = sheets_client.open_by_key(sheet_id)

    # Track last sync timestamp to avoid duplicates
    # Try to get from a metadata sheet, otherwise default to 30 days ago
    last_sync_timestamp = None
    try:
        metadata_sheet = spreadsheet.worksheet("_Metadata")
        last_sync_value = metadata_sheet.cell(2, 1).value  # Row 2, Col 1
        if last_sync_value:
            last_sync_timestamp = int(last_sync_value)
    except Exception as e:  # noqa: BLE001
        logger.info(f"No metadata sheet found, will use date-based query: {e}")

    if not last_sync_timestamp:
        one_month_ago = datetime.now(tz=timezone.utc) - timedelta(days=30)
        last_sync_timestamp = int(one_month_ago.timestamp())

    print(f"Last sync timestamp: {last_sync_timestamp}")

    emails = fetch_payment_emails(gmail, last_sync_timestamp)
    print(f"Fetched {len(emails)} emails")

    transactions = []
    latest_timestamp = last_sync_timestamp

    for msg in emails:
        txt = gmail.users().messages().get(userId="me", id=msg["id"]).execute()
        snippet = txt["snippet"]

        # Track the latest Gmail internal timestamp for next sync
        internal_date = txt.get("internalDate")
        if internal_date:
            latest_timestamp = max(latest_timestamp, int(internal_date) // 1000)

        # Extract sender email and date from headers
        headers = txt.get("payload", {}).get("headers", [])
        sender_email = ""
        email_date = ""
        for header in headers:
            if header["name"].lower() == "from":
                sender_email = header["value"]
            elif header["name"].lower() == "date":
                email_date = header["value"]

        txn = parse_email(snippet, sender_email, email_date)
        transactions.append(txn)

    print("Parsed transactions:", transactions)

    # Group transactions by month
    transactions_by_month = {}
    for txn in transactions:
        month_name = get_month_name(txn["date"])
        if month_name not in transactions_by_month:
            transactions_by_month[month_name] = []
        transactions_by_month[month_name].append(txn)

    # Append each month's transactions to its respective sheet
    for month_name, month_transactions in transactions_by_month.items():
        print(
            f"\nAppending {len(month_transactions)} transactions to '{month_name}' sheet..."
        )
        append_transactions_to_month_sheet(spreadsheet, month_name, month_transactions)

    # Update metadata with latest sync timestamp
    if transactions:
        update_sync_metadata(spreadsheet, latest_timestamp)
        print(f"\n✓ Updated sync timestamp to: {latest_timestamp}")
    else:
        print("\nNo new transactions to sync.")


if __name__ == "__main__":
    try:
        print("Starting Finance Tracker Agent...")
        run_workflow()
        print("✓ Workflow completed successfully!")
    except KeyboardInterrupt:
        print("\n✗ Workflow interrupted by user")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
    except (OSError, FileNotFoundError) as e:
        print(f"✗ File error: {e}")
    except Exception as e:
        print(f"✗ Error running workflow: {e}")
        import traceback

        traceback.print_exc()
        raise
