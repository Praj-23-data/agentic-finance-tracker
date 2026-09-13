import os

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread.utils import ValidationConditionType

try:
    from .buckets import BUCKET_OPTIONS, BUCKET_PLACEHOLDER
except ImportError:  # Support running workflow.py directly from src.
    from buckets import BUCKET_OPTIONS, BUCKET_PLACEHOLDER

# Scope: read/write access to Sheets
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

BUCKET_COLUMN = "F"
BUCKET_VALIDATION_RANGE = f"{BUCKET_COLUMN}2:{BUCKET_COLUMN}1000"


def ensure_bucket_column(worksheet):
    """Upgrade older month sheets so the Bucket column and dropdown can exist."""
    if worksheet.col_count < 6:
        worksheet.resize(cols=6)

    headers = worksheet.row_values(1)
    if len(headers) < 6 or headers[5] != "Bucket":
        worksheet.update_cell(1, 6, "Bucket")


def configure_bucket_dropdown(worksheet):
    """Apply the manual bucket dropdown to the month worksheet."""
    worksheet.add_validation(
        BUCKET_VALIDATION_RANGE,
        ValidationConditionType.one_of_list,
        BUCKET_OPTIONS,
        inputMessage="Select a bucket for this transaction.",
        strict=True,
        showCustomUi=True,
    )


def get_sheets_service():
    creds = None
    if os.path.exists("data/sheets_token.json"):
        creds = Credentials.from_authorized_user_file("data/sheets_token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "config/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        with open("data/sheets_token.json", "w") as token:
            token.write(creds.to_json())

    client = gspread.authorize(creds)
    return client


def append_transactions_to_month_sheet(spreadsheet, month_name, transactions):
    """Append transactions to a sheet named after the month (e.g., 'August 2026')."""
    if not transactions:
        print(f"No transactions to append to '{month_name}'.")
        return

    # Get or create worksheet for this month
    try:
        worksheet = spreadsheet.worksheet(month_name)
        print(f"  Using existing sheet: '{month_name}'")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=month_name, rows=1000, cols=6)
        worksheet.append_row(["Date", "Time", "Amount", "Merchant", "Source", "Bucket"])
        print(f"  Created new sheet: '{month_name}'")

    ensure_bucket_column(worksheet)
    configure_bucket_dropdown(worksheet)

    # Batch all rows into a single API call
    rows = [
        [
            txn["date"],
            txn["time"],
            txn["amount"],
            txn["merchant"],
            txn["source"],
            BUCKET_PLACEHOLDER,
        ]
        for txn in transactions
    ]
    worksheet.append_rows(rows)
    print(f"  ✓ Appended {len(rows)} transactions to '{month_name}'")
