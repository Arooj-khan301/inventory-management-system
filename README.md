# Inventory Management Service (MIS)

**Repository:** `inventory-management-system`  
**Author:** Arooj Khan (BS in Computer Science Semester Project, The University of Haripur)  
**Stack:** Python, Flask, SQLite, HTML5, CSS3, Bootstrap 5

## 1. Overview

A lightweight Management Information System (MIS) designed for real-time warehouse product cataloging, stock-level monitoring, low-stock threshold alerts, and Stock-IN / Stock-OUT ledger transactions.

## 2. Implemented Features

- **Warehouse Overview Dashboard (`/`):** Displays total distinct products, total units in stock, total inventory valuation (PKR), low-stock alert count (`quantity <= reorder_level`), and the 5 most recent stock transactions.
- **Product Catalog & Search (`/products`):** Lists all products with SKU codes, category labels, current quantities, unit prices, and dynamic *In Stock* / *Low Stock* badges, with keyword search by product name or SKU.
- **Product CRUD (`/products/add`, `/products/edit/<id>`, `/products/delete/<id>`):** Add new products with unique SKUs, edit pricing and reorder thresholds, and remove discontinued items.
- **Stock-IN / Stock-OUT Ledger (`/stock/adjust/<id>`):** Record incoming stock shipments (`IN`) and outgoing dispatches (`OUT`) with validation preventing negative stock balances.

## 3. Repository Structure

```text
inventory-management-system/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                     # Flask application & SQLite database routes
├── schema.sql                 # Normalized SQLite schema & initial seed records
├── templates/
│   ├── base.html              # Master navigation & layout template
│   ├── index.html             # KPI dashboard & recent transaction log
│   ├── products.html          # Searchable product catalog table
│   ├── product_form.html      # Add / Edit product form
│   └── stock_adjust.html      # Stock IN / OUT adjustment form
└── tests/
    └── test_inventory.py      # In-memory SQLite unit tests for schema & CRUD
```

## 4. Installation & Quick Start

```bash
git clone https://github.com/Arooj-khan301/inventory-management-system.git
cd inventory-management-system
pip install -r requirements.txt

# Run unit tests
python3 -m unittest discover -s tests -v

# Start the Flask web server (auto-initializes inventory.db from schema.sql)
python3 app.py
```
Then open `http://localhost:5000` in your browser.
