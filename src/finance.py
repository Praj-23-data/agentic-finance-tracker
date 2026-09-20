from numbers import Real
from datetime import datetime


def _month_sort_key(month):
    try:
        return datetime.strptime(month, "%B %Y")
    except (TypeError, ValueError):
        return datetime.min


def available_months(transactions):
    """Return distinct worksheet months in reverse display order."""
    months = {row.get("Month", "") for row in transactions if row.get("Month")}
    return sorted(months, key=_month_sort_key, reverse=True)


def filter_transactions(transactions, month="All months", bucket="All buckets"):
    """Filter transaction rows without mutating the source collection."""
    return [
        row
        for row in transactions
        if (month == "All months" or row.get("Month") == month)
        and (bucket == "All buckets" or row.get("Bucket") == bucket)
    ]


def total_amount(transactions):
    """Sum valid numeric transaction amounts."""
    total = 0.0
    for row in transactions:
        amount = row.get("Amount")
        if isinstance(amount, Real) and not isinstance(amount, bool):
            total += amount
        elif isinstance(amount, str):
            try:
                total += float(amount.replace(",", "").replace("INR", "").strip())
            except ValueError:
                continue
    return total
