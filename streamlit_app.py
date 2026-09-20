import os

import streamlit as st

from src.finance import available_months, filter_transactions, total_amount
from src.sheets_agent import (
    get_sheets_service,
    get_transactions_from_spreadsheet,
)

DEFAULT_SHEET_ID = "1HpfqX5ds6xCc5dWTcgRFeFwVU8HFgDRQSrgda35V1Hs"

st.set_page_config(page_title="Finance Tracker", page_icon="$", layout="wide")
st.title("Finance Tracker")
st.caption("Transactions synced from Google Sheets")

sheet_id = os.getenv("GOOGLE_SHEET_ID", DEFAULT_SHEET_ID)


@st.cache_data(ttl=60, show_spinner="Loading transactions...")
def load_transactions(sheet_id):
    sheets_client = get_sheets_service()
    spreadsheet = sheets_client.open_by_key(sheet_id)
    return get_transactions_from_spreadsheet(spreadsheet)


if st.button("Refresh data"):
    load_transactions.clear()
    st.rerun()

try:
    transactions = load_transactions(sheet_id)
except Exception as error:  # noqa: BLE001
    st.error(f"Could not load transactions: {error}")
    st.info("Check config/credentials.json, Google OAuth access, and GOOGLE_SHEET_ID.")
    st.stop()

months = available_months(transactions)
buckets = sorted({row.get("Bucket", "") for row in transactions if row.get("Bucket")})
selected_month = st.selectbox("Month", ["All months", *months])
selected_bucket = st.selectbox("Bucket", ["All buckets", *buckets])

visible_transactions = filter_transactions(
    transactions, month=selected_month, bucket=selected_bucket
)

st.metric("Transactions", len(visible_transactions))
st.metric("Total amount", f"INR {total_amount(visible_transactions):,.2f}")
if visible_transactions:
    st.dataframe(visible_transactions, use_container_width=True, hide_index=True)
else:
    st.info("No transactions found for this selection.")
