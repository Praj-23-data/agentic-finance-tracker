import unittest
from unittest.mock import Mock

from src.buckets import BUCKET_OPTIONS, BUCKET_PLACEHOLDER
from src.sheets_agent import (
    BUCKET_VALIDATION_RANGE,
    append_transactions_to_month_sheet,
)


class SheetBucketTests(unittest.TestCase):
    def test_legacy_sheet_is_expanded_before_validation(self):
        spreadsheet = Mock()
        worksheet = Mock()
        worksheet.col_count = 5
        worksheet.row_values.return_value = [
            "Date",
            "Time",
            "Amount",
            "Merchant",
            "Source",
        ]
        spreadsheet.worksheet.return_value = worksheet

        append_transactions_to_month_sheet(
            spreadsheet,
            "September 2026",
            [{
                "date": "13-09-2026",
                "time": "10:30",
                "amount": 100.0,
                "merchant": "Test Merchant",
                "source": "Test Bank",
            }],
        )

        worksheet.resize.assert_called_once_with(cols=6)
        worksheet.update_cell.assert_called_once_with(1, 6, "Bucket")

    def test_appended_transactions_start_with_manual_bucket_placeholder(self):
        spreadsheet = Mock()
        worksheet = Mock()
        worksheet.col_count = 6
        worksheet.row_values.return_value = [
            "Date",
            "Time",
            "Amount",
            "Merchant",
            "Source",
            "Bucket",
        ]
        spreadsheet.worksheet.return_value = worksheet
        transaction = {
            "date": "13-09-2026",
            "time": "10:30",
            "amount": 100.0,
            "merchant": "Test Merchant",
            "source": "Test Bank",
        }

        append_transactions_to_month_sheet(spreadsheet, "September 2026", [transaction])

        worksheet.add_validation.assert_called_once_with(
            BUCKET_VALIDATION_RANGE,
            unittest.mock.ANY,
            BUCKET_OPTIONS,
            inputMessage="Select a bucket for this transaction.",
            strict=True,
            showCustomUi=True,
        )
        worksheet.append_rows.assert_called_once_with(
            [
                [
                    transaction["date"],
                    transaction["time"],
                    transaction["amount"],
                    transaction["merchant"],
                    transaction["source"],
                    BUCKET_PLACEHOLDER,
                ]
            ]
        )


if __name__ == "__main__":
    unittest.main()