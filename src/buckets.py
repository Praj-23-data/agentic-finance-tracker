"""User-editable expense buckets."""

BUCKET_PLACEHOLDER = "Please select bucket"

# Add new names to this list to make them available in the Google Sheets dropdown.
BUCKET_OPTIONS = [
    "Rent",
    "Petrol",
    "DailyExpenses",
    "Beta",
]

# Retained for callers that still use the optional classifier directly. The
# workflow uses BUCKET_OPTIONS and requires manual selection in Sheets.
BUCKET_RULES = {
    "Housing": ("rent", "maintenance", "society"),
    "Food & Dining": (
        "swiggy",
        "zomato",
        "restaurant",
        "dominos",
    ),
    "Transportation": ("uber", "ola", "rapido", "metro", "petrol", "fuel"),
    "Bills & Utilities": (
        "electricity",
        "water bill",
        "internet",
        "broadband",
        "mobile recharge",
        "insurance",
    ),
    "Healthcare": ("pharmacy", "hospital", "apollo", "medplus", "clinic"),
    "Entertainment": ("netflix", "spotify", "movie", "bookmyshow", "prime video"),
    "Shopping": ("amazon", "flipkart", "myntra", "retail", "mall"),
}

DEFAULT_BUCKET = "Other"
