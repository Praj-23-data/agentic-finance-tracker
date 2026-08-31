import re
from datetime import datetime
from email.utils import parsedate_to_datetime


def determine_source(sender_email: str, snippet: str) -> str:
    """
    Determine the source bank based on sender email and email content.
    If snippet contains 'Credit Card', append it to the bank name.
    """
    # Map email senders to bank names
    if "axis.bank.in" in sender_email.lower():
        source = "Axis Bank"
    elif "icici.bank.in" in sender_email.lower():
        source = "ICICI Bank"
    else:
        source = "Unknown Bank"

    # Check if it's a credit card transaction
    if "credit card" in snippet.lower():
        source += " Credit Card"

    return source


def extract_time_from_email_date(email_date: str) -> str:
    """Extract time (HH:MM:SS) from email Date header."""
    if not email_date:
        return "00:00:00"

    try:
        dt = parsedate_to_datetime(email_date)
        return dt.strftime("%H:%M:%S")
    except (TypeError, ValueError):
        return "00:00:00"


def parse_email(snippet: str, sender_email: str = "", email_date: str = ""):
    """
    Extracts date, amount, merchant, time, and source from a bank alert email snippet.
    Returns a dict with keys: date, amount, merchant, source, time.
    """

    # Example Axis/ICICI alert formats:
    # "Your account XXXX was debited INR 1,250.00 at Amazon on 31-08-2026"
    # "INR 500.00 spent on Swiggy on 30-08-2026"

    # Amount (INR with commas/decimals) - convert to float for proper data type
    amount_match = re.search(r"INR\s?([\d,]+\.?\d*)", snippet, re.IGNORECASE)
    amount = float(amount_match.group(1).replace(",", "")) if amount_match else None

    # Merchant (word after 'at' or 'on')
    merchant_match = re.search(r"(?:at|on)\s+([A-Za-z0-9 &]+)", snippet)
    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown"

    # Date (dd-mm-yyyy)
    date_match = re.search(r"(\d{2}-\d{2}-\d{4})", snippet)
    date = date_match.group(1) if date_match else datetime.today().strftime("%d-%m-%Y")  # noqa: DTZ002

    # Source (based on sender email and content)
    source = determine_source(sender_email, snippet)

    # Time (extracted from email Date header)
    time = extract_time_from_email_date(email_date)

    return {
        "date": date,
        "amount": amount,
        "merchant": merchant,
        "source": source,
        "time": time,
    }
