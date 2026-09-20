import unittest

from src.finance import available_months, filter_transactions, total_amount


class FinanceLogicTests(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            {"Month": "September 2026", "Bucket": "Food", "Amount": 125.5},
            {"Month": "September 2026", "Bucket": "Travel", "Amount": 300},
            {"Month": "August 2026", "Bucket": "Food", "Amount": None},
        ]

    def test_available_months_are_unique_and_reverse_sorted(self):
        self.transactions.append(
            {"Month": "December 2025", "Bucket": "Food", "Amount": 10}
        )
        self.assertEqual(
            available_months(self.transactions),
            ["September 2026", "August 2026", "December 2025"],
        )

    def test_filter_supports_month_and_bucket_together(self):
        filtered = filter_transactions(
            self.transactions, month="September 2026", bucket="Food"
        )

        self.assertEqual(filtered, [self.transactions[0]])

    def test_filter_does_not_mutate_source_rows(self):
        filtered = filter_transactions(self.transactions)

        self.assertIsNot(filtered, self.transactions)
        self.assertEqual(len(self.transactions), 3)

    def test_total_amount_ignores_missing_amounts(self):
        self.assertEqual(total_amount(self.transactions), 425.5)

    def test_total_amount_accepts_formatted_strings(self):
        self.assertEqual(total_amount([{"Amount": "INR 1,250.50"}]), 1250.5)


if __name__ == "__main__":
    unittest.main()
