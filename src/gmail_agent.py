import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None
    if os.path.exists("data/token.json"):
        creds = Credentials.from_authorized_user_file("data/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "config/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("data/token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def date_to_unix(date_str):
    # parse date and make it timezone-aware (UTC) to avoid naive datetime issues
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
        tzinfo=datetime.timezone.utc
    )
    return int(dt.timestamp())


def fetch_payment_emails(service, last_sync_timestamp):
    """
    Fetch payment emails after the given Unix timestamp.
    Uses timestamp to avoid duplicates on subsequent runs.
    """
    query = f"(from:alerts@axis.bank.in OR from:alert@icici.bank.in) after:{last_sync_timestamp}"
    results = service.users().messages().list(userId="me", q=query).execute()
    return results.get("messages", [])
