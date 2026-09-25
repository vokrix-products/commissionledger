import unittest
from processor import process_file

class ProcessorTests(unittest.TestCase):
    def test_csv_extraction(self):
        data = b"supplier,product,price\nAcme,Widget,9.99"
        records = process_file(data)
        self.assertIsInstance(records, list)
        self.assertTrue(len(records) > 0)
        self.assertEqual(records[0]["details"].get("manufacturer_supplier_name"), "Acme")
        self.assertEqual(records[0]["title"], "Acme")

    def test_empty_bytes(self):
        self.assertEqual(process_file(b""), [])

    def test_fallback_text(self):
        records = process_file(b"Payer: VendorCo\nAmount: 100\n")
        self.assertIsInstance(records, list)
        self.assertTrue(len(records) > 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
