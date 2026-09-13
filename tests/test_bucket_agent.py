import unittest

from src.bucket_agent import DEFAULT_BUCKET, classify_expense, classify_transaction


class ClassifyExpenseTests(unittest.TestCase):
    def test_matches_merchant_case_insensitively(self):
        self.assertEqual(classify_expense("Swiggy Instamart"), "Food & Dining")

    def test_matches_multi_word_keyword(self):
        self.assertEqual(classify_expense("My Broadband Provider"), "Bills & Utilities")

    def test_unknown_merchant_uses_explicit_fallback(self):
        self.assertEqual(classify_expense("Local Store"), DEFAULT_BUCKET)

    def test_empty_merchant_uses_explicit_fallback(self):
        self.assertEqual(classify_expense(None), DEFAULT_BUCKET)


class ClassifyTransactionTests(unittest.TestCase):
    def test_enriches_without_mutating_original_transaction(self):
        transaction = {"merchant": "Uber", "amount": 250.0}

        enriched = classify_transaction(transaction)

        self.assertEqual(enriched["bucket"], "Transportation")
        self.assertNotIn("bucket", transaction)


if __name__ == "__main__":
    unittest.main()