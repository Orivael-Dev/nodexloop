import unittest
from checkout import total_cents

class CheckoutTests(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(total_cents([{"quantity": 2, "unit_cents": 199}]), 398)

    def test_discount_rounds_down(self):
        self.assertEqual(total_cents([{"quantity": 1, "unit_cents": 99}], 50), 49)

    def test_multiple_items(self):
        items = [{"quantity": 3, "unit_cents": 101}, {"quantity": 1, "unit_cents": 99}]
        self.assertEqual(total_cents(items, 25), 301)

    def test_zero(self):
        self.assertEqual(total_cents([], 0), 0)
