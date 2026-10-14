import csv
from itertools import product
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from xml.parsers.expat import errors

# 1. CAU HINH

random.seed(42)  # Giup sinh lai du lieu co the lap lai

OUTPUT_DIR = Path("output")

COUNTS = {
    "Category": 20,
    "Store": 20,
    "Customer": 2000,
    "Product": 1000,
    "Order": 2500,
    "OrderItem": 3000,
    "Payment": 1460,
}

assert sum(COUNTS.values()) == 10000

#2. CAC HAM HO TRO

def make_id(prefix, number):
    """Tao ma duy nhat, vi du CUST000001."""
    return f"{prefix}{number:06d}"


def random_date(start_date, end_date):
    """Sinh ngay ngau nhien trong khoang cho truoc."""
    days = (end_date - start_date).days
    result = start_date + timedelta(days=random.randint(0, days))
    return result.isoformat() + "T10:00:00Z"


def money(value):
    """Lam tron tien den 2 chu so thap phan."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def export_csv_json(table_name, rows):
    """Xuat mot thuc the ra ca CSV va JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / f"{table_name}.csv"
    json_path = OUTPUT_DIR / f"{table_name}.json"

    # Ghi CSV
    if rows:
        with csv_path.open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=list(rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(rows)

    # Ghi JSON
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(
            rows,
            file,
            ensure_ascii=False,
            indent=2,
            default=lambda value: float(value)
            if isinstance(value, Decimal)
            else str(value),
        )

    print(f"Da xuat {table_name}: {len(rows)} ban ghi")

#3. SINH CATOGORI va STORE

category_names = [
    "Laptop", "Dien thoai", "May tinh bang", "Man hinh",
    "Ban phim", "Chuot", "Tai nghe", "Loa",
    "May in", "Phu kien", "Thiet bi mang", "Camera",
    "Luu tru", "Linh kien", "Sac", "Day cap",
    "Dong ho", "Thiet bi gia dung", "Van phong pham",
    "San pham khac",
]

def generate_categories():
    
    categories = []
    for i in range(1, COUNTS["Category"] + 1):
        category = {
            "category_id": make_id("CAT", i),
            "name": random.choice(category_names),
            "description": f"Mô tả cho Category {i}",
        }
        categories.append(category)
    return categories

def generate_stores():
    stores = []

    streets = [
        "Le Loi", "Nguyen Trai", "Tran Hung Dao",
        "Hai Ba Trung", "Pham Van Dong", "Vo Nguyen Giap"
    ]

    districts = [
        "Ba Dinh", "Cau Giay", "Dong Da",
        "Hai Ba Trung", "Hoan Kiem"
    ]

    cities = [
        "Ha Noi", "Da Nang", "Ho Chi Minh"
    ]

    for i in range(1, COUNTS["Store"] + 1):
        store = {
            "store_id": make_id("STORE", i),
            "name": f"Store {i}",
            "location": (
                f"{random.randint(1, 300)} "
                f"{random.choice(streets)}, "
                f"{random.choice(districts)}, "
                f"{random.choice(cities)}, Viet Nam"
            ),
        }

        stores.append(store)

    return stores

#4. SINH CUSTOMER
first_names = [
    "Nguyen Van", "Tran Thi", "Le Van", "Pham Thi",
    "Hoang Van", "Phan Thi", "Vu Minh", "Do Ngoc",
    "Bui Thanh", "Dang Thu",
]

last_names = [
    "An", "Binh", "Chi", "Dung", "Giang", "Ha",
    "Hanh", "Linh", "Minh", "Nam", "Phuong",
    "Quan", "Trang", "Tuan", "Vy",
]

def generate_customers():
    customers = []
    for i in range(1, COUNTS["Customer"] + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer = {
            "customer_id": make_id("CUST", i),
            "name": f"{first_name} {last_name}",
            "email": f"{last_name.lower().replace(' ', '')}_{first_name.lower().replace(' ', '')}{i:06d}@example.com",
            "phone_number": f"09{random.randint(10000000, 99999999)}",
        }
        customers.append(customer)
    return customers

#5. SINH PRODUCT
product_names = [
    "Laptop", "Smartphone", "Tablet", "Monitor",
    "Keyboard", "Mouse", "Headphone", "Speaker",
    "Printer", "Router", "Webcam", "SSD",
]

def generate_products(categories):
    products = []
    for i in range(1, COUNTS["Product"] + 1):
        category = random.choice(categories)
        product = {
            "product_id": make_id("PROD", i),
            "name": f"{random.choice(product_names)} {i}",
            "category_id": category["category_id"],
            "price": money(random.uniform(100, 2000)),
        }
        products.append(product)
    return products

#6, SINH ORDER va ORDERITEM

start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 9, 30)

def generate_orders(customers, stores, products):
    orders = []
    order_items = []

    for i in range(1, COUNTS["Order"] + 1):
        order_id = make_id("ORD", i)

        # Tao dung 1750 order completed
        if i <= 1750:
            status = "completed"
        elif i <= 2250:
            status = "pending"
        else:
            status = "canceled"

        order = {
            "order_id": order_id,
            "customer_id": random.choice(customers)["customer_id"],
            "store_id": random.choice(stores)["store_id"],
            "order_date": random_date(start_date, end_date),
            "status": status,
            "total_amount": Decimal("0.00"),
        }

        # 500 order dau co 2 item;
        # 2000 order con lai co 1 item.
        number_of_items = 2 if i <= 500 else 1
        total = Decimal("0.00")

        for _ in range(number_of_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product["price"]

            order_items.append({
                "order_item_id": make_id(
                    "ITEM", len(order_items) + 1
                ),
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": quantity,
                "uniprice": unit_price,
            })

            total += unit_price * quantity

        order["total_amount"] = money(total)
        orders.append(order)

    return orders, order_items


#7. SINH PAYMENT
def generate_payments(orders):
    completed_orders = [
        order for order in orders
        if order["status"] == "completed"
    ]

    paid_orders = random.sample(
        completed_orders, COUNTS["Payment"]
    )

    payments = []

    for i, order in enumerate(paid_orders, start=1):
        payments.append({
            "payment_id": make_id("PAY", i),
            "order_id": order["order_id"],
            "payment_date": order["order_date"],
            "amount": order["total_amount"],
            "payment_method": random.choice([
                "Tien mat",
                "The tin dung",
                "Chuyen khoan",
            ]),
        })

    return payments

#8. KIEM TRA VA XUAT DU LIEU
def validate_data(tables):
    errors = []

    # Kiem tra tong so ban ghi
    total_rows = sum(len(rows) for rows in tables.values())

    if total_rows != 10000:
        errors.append(
            f"Tong ban ghi la {total_rows}, khong phai 10000"
        )

    # Ten khoa chinh cua tung thuc the
    pk_fields = {
        "Category": "category_id",
        "Store": "store_id",
        "Customer": "customer_id",
        "Product": "product_id",
        "Order": "order_id",
        "OrderItem": "order_item_id",
        "Payment": "payment_id",
    }

    # Kiem tra khoa chinh va gia tri rong
    for table_name, rows in tables.items():
        key = pk_fields[table_name]
        values = [row[key] for row in rows]

        if len(values) != len(set(values)):
            errors.append(f"{table_name}: khoa chinh bi trung")

        for row_number, row in enumerate(rows, start=1):
            for field, value in row.items():
                if value is None or value == "":
                    errors.append(
                        f"{table_name}, dong {row_number}: "
                        f"{field} bi rong"
                    )

    # Kiem tra email duy nhat
    emails = [
        row["email"] for row in tables["Customer"]
        if row["email"]
    ]

    if len(emails) != len(set(emails)):
        errors.append("Customer: email bi trung")

    # Tap hop khoa de kiem tra foreign key
    category_ids = {
        row["category_id"] for row in tables["Category"]
    }
    store_ids = {
        row["store_id"] for row in tables["Store"]
    }
    customer_ids = {
        row["customer_id"] for row in tables["Customer"]
    }
    product_ids = {
        row["product_id"] for row in tables["Product"]
    }
    order_ids = {
        row["order_id"] for row in tables["Order"]
    }

    # Product -> Category
    for product in tables["Product"]:
        if product["category_id"] not in category_ids:
            errors.append("Product: category_id khong ton tai")
        if product["price"] < 0:
            errors.append("Product: price am")

    # Order -> Customer, Store
    for order in tables["Order"]:
        if order["customer_id"] not in customer_ids:
            errors.append("Order: customer_id khong ton tai")
        if order["store_id"] not in store_ids:
            errors.append("Order: store_id khong ton tai")
        if order["status"] not in {
            "pending", "completed", "canceled"
        }:
            errors.append("Order: status khong hop le")
        if order["total_amount"] < 0:
            errors.append("Order: total_amount am")

    # OrderItem -> Order, Product
    for item in tables["OrderItem"]:
        if item["order_id"] not in order_ids:
            errors.append("OrderItem: order_id khong ton tai")
        if item["product_id"] not in product_ids:
            errors.append("OrderItem: product_id khong ton tai")
        if item["quantity"] <= 0:
            errors.append("OrderItem: quantity phai > 0")
        if item["uniprice"] < 0:
            errors.append("OrderItem: uniprice am")

    # Payment -> Order
    for payment in tables["Payment"]:
        if payment["order_id"] not in order_ids:
            errors.append("Payment: order_id khong ton tai")
        if payment["amount"] < 0:
            errors.append("Payment: amount am")

    # Tong Order = tong quantity * uniprice
    totals = {}

    for item in tables["OrderItem"]:
        order_id = item["order_id"]
        line_total = item["uniprice"] * item["quantity"]

        totals[order_id] = totals.get(
            order_id, Decimal("0.00")
        ) + line_total

    for order in tables["Order"]:
        calculated = money(
            totals.get(order["order_id"], Decimal("0.00"))
        )

        if calculated != order["total_amount"]:
            errors.append(
                f"Order {order['order_id']}: total_amount sai"
            )

    # Payment trong bo du lieu nay phai thuoc order completed
    for payment in tables["Payment"]:
        order = next(
            (
                row for row in tables["Order"]
                if row["order_id"] == payment["order_id"]
            ),
            None,
        )

        if order is not None and order["status"] != "completed":
            errors.append(
                f"Payment {payment['payment_id']}: "
                "Order chua completed"
            )

    if errors:
        print("\nDU LIEU CO LOI:")
        for error in errors[:20]:
            print("-", error)

        print("Tong so loi:", len(errors))
        raise ValueError("Khong xuat file vi du lieu chua hop le.")

    print("Kiem tra du lieu: DAT")

#9. XUAT DU LIEU
if __name__ == "__main__":
    categories = generate_categories()
    stores = generate_stores()
    customers = generate_customers()
    products = generate_products(categories)

    orders, order_items = generate_orders(
        customers, stores, products
    )

    payments = generate_payments(orders)

    all_tables = {
        "Category": categories,
        "Store": stores,
        "Customer": customers,
        "Product": products,
        "Order": orders,
        "OrderItem": order_items,
        "Payment": payments,
    }

    validate_data(all_tables)

    for table_name, rows in all_tables.items():
        export_csv_json(table_name, rows)

    print("\nHOAN TAT!")
    print("Tong so ban ghi:", sum(
        len(rows) for rows in all_tables.values()
    ))
    print("Thu muc ket qua:", OUTPUT_DIR.resolve())
