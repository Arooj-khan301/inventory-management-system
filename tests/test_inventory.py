"""Unit tests for Inventory Management System SQLite schema and CRUD logic."""

import os
import sqlite3
import unittest


class TestInventorySchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())

    def tearDown(self):
        self.conn.close()

    def test_seed_data_loaded(self):
        cat_count = self.conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        prod_count = self.conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        self.assertEqual(cat_count, 3)
        self.assertEqual(prod_count, 3)

    def test_product_crud_and_stock_adjustment(self):
        self.conn.execute(
            "INSERT INTO products (name, sku, category_id, quantity, unit_price, reorder_level) VALUES (?, ?, ?, ?, ?, ?)",
            ("USB-C Hub", "ELEC-HUB-04", 1, 20, 3500.0, 5),
        )
        row = self.conn.execute(
            "SELECT * FROM products WHERE sku = 'ELEC-HUB-04'"
        ).fetchone()
        self.assertEqual(row["quantity"], 20)

        # Simulate Stock OUT of 5 units
        self.conn.execute(
            "UPDATE products SET quantity = quantity - 5 WHERE id = ?", (row["id"],)
        )
        updated = self.conn.execute(
            "SELECT quantity FROM products WHERE id = ?", (row["id"],)
        ).fetchone()[0]
        self.assertEqual(updated, 15)


if __name__ == "__main__":
    unittest.main()
