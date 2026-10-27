"""Inventory Management Service (MIS).

Author: Arooj Khan (BSCS Semester Project, The University of Haripur)
Stack: Python, Flask, SQLite, HTML5, CSS3, Bootstrap 5
"""

import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "inventory-secret-key-2026")
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")
app.config["DATABASE"] = os.getenv("INVENTORY_DB_PATH", DEFAULT_DB_PATH)


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def ensure_db():
    if app.config["DATABASE"] != ":memory:" and not os.path.exists(app.config["DATABASE"]):
        init_db()


@app.route("/")
def index():
    ensure_db()
    conn = get_db()
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_stock = conn.execute("SELECT COALESCE(SUM(quantity), 0) FROM products").fetchone()[0]
    total_value = conn.execute(
        "SELECT COALESCE(SUM(quantity * unit_price), 0) FROM products"
    ).fetchone()[0]
    low_stock = conn.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= reorder_level"
    ).fetchone()[0]
    recent = conn.execute("""
        SELECT t.*, p.name as product_name, p.sku
        FROM transactions t JOIN products p ON t.product_id = p.id
        ORDER BY t.created_at DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template(
        "index.html",
        total_products=total_products,
        total_stock=total_stock,
        total_value=total_value,
        low_stock=low_stock,
        recent_transactions=recent,
    )


@app.route("/products")
def products():
    ensure_db()
    search = request.args.get("search", "").strip()
    conn = get_db()
    if search:
        items = conn.execute(
            """
            SELECT p.*, c.name as category_name
            FROM products p LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE ? OR p.sku LIKE ?
            ORDER BY p.name ASC
            """,
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        items = conn.execute("""
            SELECT p.*, c.name as category_name
            FROM products p LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.name ASC
        """).fetchall()
    conn.close()
    return render_template("products.html", products=items, search=search)


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    ensure_db()
    conn = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        sku = request.form["sku"].strip().upper()
        category_id = int(request.form["category_id"])
        quantity = int(request.form["quantity"])
        unit_price = float(request.form["unit_price"])
        reorder_level = int(request.form["reorder_level"])
        try:
            conn.execute(
                """
                INSERT INTO products (name, sku, category_id, quantity, unit_price, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, sku, category_id, quantity, unit_price, reorder_level),
            )
            conn.commit()
            conn.close()
            flash("Product registered successfully!", "success")
            return redirect(url_for("products"))
        except sqlite3.IntegrityError:
            flash(f"SKU '{sku}' already exists.", "danger")
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    conn.close()
    return render_template("product_form.html", product=None, categories=categories)


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    ensure_db()
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        return redirect(url_for("products"))
    if request.method == "POST":
        name = request.form["name"].strip()
        category_id = int(request.form["category_id"])
        unit_price = float(request.form["unit_price"])
        reorder_level = int(request.form["reorder_level"])
        conn.execute(
            """
            UPDATE products
            SET name = ?, category_id = ?, unit_price = ?, reorder_level = ?
            WHERE id = ?
            """,
            (name, category_id, unit_price, reorder_level, product_id),
        )
        conn.commit()
        conn.close()
        flash("Product updated successfully!", "success")
        return redirect(url_for("products"))
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    conn.close()
    return render_template("product_form.html", product=product, categories=categories)


@app.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    ensure_db()
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash("Product deleted.", "info")
    return redirect(url_for("products"))


@app.route("/stock/adjust/<int:product_id>", methods=["GET", "POST"])
def adjust_stock(product_id):
    ensure_db()
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        return redirect(url_for("products"))
    if request.method == "POST":
        action = request.form["action"]
        qty = int(request.form["quantity"])
        notes = request.form.get("notes", "").strip()
        new_qty = product["quantity"] + qty if action == "IN" else product["quantity"] - qty
        if new_qty >= 0:
            conn.execute(
                "UPDATE products SET quantity = ? WHERE id = ?", (new_qty, product_id)
            )
            conn.execute(
                """
                INSERT INTO transactions (product_id, transaction_type, quantity, notes)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, action, qty, notes),
            )
            conn.commit()
            conn.close()
            flash("Stock adjusted!", "success")
            return redirect(url_for("products"))
        flash("Insufficient stock for OUT adjustment.", "danger")
    conn.close()
    return render_template("stock_adjust.html", product=product)


if __name__ == "__main__":
    ensure_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
