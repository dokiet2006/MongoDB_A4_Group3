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



BATCH_SIZE = 10_000

DATA_SIZES = {
    "100K": {
        "Category": 20,
        "Store": 20,
        "Customer": 20_000,
        "Product": 2_000,
        "Order": 100_000,
    },
    "1M": {
        "Category": 50,
        "Store": 100,
        "Customer": 200_000,
        "Product": 20_000,
        "Order": 1_000_000,
    },
    "5M": {
        "Category": 100,
        "Store": 500,
        "Customer": 1_000_000,
        "Product": 100_000,
        "Order": 5_000_000,
    }
}

SIZE = "100K"  # Có thể đổi thành "1M" hoặc "5M"
OUTPUT_DIR = Path("output") / SIZE
COUNTS = DATA_SIZES[SIZE]

ORDER_COUNT = COUNTS["Order"]
COMPLETED_COUNT = int(ORDER_COUNT * 0.7)
PENDING_COUNT = int(ORDER_COUNT * 0.2)
CANCELED_COUNT = ORDER_COUNT - COMPLETED_COUNT - PENDING_COUNT

COUNTS["OrderItem"] = int(ORDER_COUNT * 1.2)
COUNTS["Payment"] = int(COMPLETED_COUNT * 1460 / 1750)

#2. CAC HAM HO TRO

def make_id(prefix, number):
    """Tao ma duy nhat, vi du CUST000001."""
    return f"{prefix}{number:06d}"


def random_date(start_date, end_date):
    """Sinh ngay ngau nhien trong khoang cho truoc."""
    days = (end_date - start_date).days
    result = start_date + timedelta(days=random.randint(0, days))
    return result.strftime("%Y-%m-%dT10:00:00Z")


def money(value):
    """Lam tron tien den 2 chu so thap phan."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def initialize_export(table_name, fieldnames):
    """Khoi tao file CSV va JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / f"{table_name}.csv"
    json_path = OUTPUT_DIR / f"{table_name}.json"

    # Khoi tao file CSV va ghi header
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    # Khoi tao file JSON
    with json_path.open("w", encoding="utf-8") as file:
        file.write("[")

    return {
        "table_name": table_name,
        "csv_path": csv_path,
        "json_path": json_path,
        "fieldnames": fieldnames,
        "first_json": True,
        "count": 0,
    }


def append_export(export_info, rows):
    """Ghi them mot batch vao CSV va JSON."""

    if not rows:
        return

    # Ghi them vao CSV
    with export_info["csv_path"].open(
        "a", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=export_info["fieldnames"]
        )
        writer.writerows(rows)

    # Ghi them vao JSON
    with export_info["json_path"].open("a", encoding="utf-8") as file:
        for row in rows:
            if not export_info["first_json"]:
                file.write(",")

            json.dump(
                row,
                file,
                ensure_ascii=False,
                default=lambda value: float(value)
                if isinstance(value, Decimal)
                else str(value),
            )

            export_info["first_json"] = False

    export_info["count"] += len(rows)


def finalize_export(export_info):
    """Hoan tat file JSON va thong bao ket qua."""

    with export_info["json_path"].open("a", encoding="utf-8") as file:
        file.write("]")

    print(
        f"Da xuat {export_info['table_name']}: "
        f"{export_info['count']} ban ghi"
    )


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
    customers_batch = []

    for i in range(1, COUNTS["Customer"] + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        customer = {
            "customer_id": make_id("CUST", i),
            "name": f"{first_name} {last_name}",
            "email": f"{last_name.lower().replace(' ', '')}_{first_name.lower().replace(' ', '')}{i:06d}@example.com",
            "phone_number": f"09{random.randint(10000000, 99999999)}",
        }

        customers_batch.append(customer)

        if len(customers_batch) >= BATCH_SIZE:
            yield customers_batch
            customers_batch = []

    if customers_batch:
        yield customers_batch


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

def generate_orders(stores, products):
    orders_batch = []
    order_items_batch = []

    # Tong so Order co 2 items
    two_item_count = int(ORDER_COUNT * 0.2)

    # Dem ID cua OrderItem
    item_number = 0

    for i in range(1, COUNTS["Order"] + 1):
        order_id = make_id("ORD", i)

        # Phan bo trang thai Order
        if i <= COMPLETED_COUNT:
            status = "completed"
        elif i <= COMPLETED_COUNT + PENDING_COUNT:
            status = "pending"
        else:
            status = "canceled"

        order = {
            "order_id": order_id,
            "customer_id": make_id(
                "CUST",
                random.randint(1, COUNTS["Customer"])
            ),
            "store_id": random.choice(stores)["store_id"],
            "order_date": random_date(start_date, end_date),
            "status": status,
            "total_amount": Decimal("0.00"),
        }

        # 20% Order co 2 items, 80% co 1 item
        number_of_items = 2 if i <= two_item_count else 1

        total = Decimal("0.00")

        for _ in range(number_of_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product["price"]

            item_number += 1

            order_items_batch.append({
                "order_item_id": make_id("ITEM", item_number),
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": quantity,
                "uniprice": unit_price,
            })

            total += unit_price * quantity

        order["total_amount"] = money(total)
        orders_batch.append(order)

        # Khi du 10.000 Order thi tra ve mot batch
        if len(orders_batch) >= BATCH_SIZE:
            yield orders_batch, order_items_batch

            # Tao batch moi
            orders_batch = []
            order_items_batch = []

    # Tra ve batch cuoi neu con du lieu
    if orders_batch:
        yield orders_batch, order_items_batch



#7. SINH PAYMENT
def create_payment(order, payment_number):
    """Tao Payment cho mot Order."""

    return {
        "payment_id": make_id("PAY", payment_number),
        "order_id": order["order_id"],
        "payment_date": order["order_date"],
        "amount": order["total_amount"],
        "payment_method": random.choice([
            "Tien mat",
            "The tin dung",
            "Chuyen khoan",
        ]),
    }


def validate_batch(orders, order_items, payments,
                   store_ids, product_ids):

    errors = []

    # Tao tap hop ID cua Order trong batch
    batch_order_ids = {
        order["order_id"] for order in orders
    }

    # Tinh tong tien Order tu cac OrderItem
    totals = {}

    for item in order_items:
        if item["order_id"] not in batch_order_ids:
            errors.append("OrderItem: order_id khong ton tai")

        if item["product_id"] not in product_ids:
            errors.append("OrderItem: product_id khong ton tai")

        if item["quantity"] <= 0:
            errors.append("OrderItem: quantity phai > 0")

        if item["uniprice"] < 0:
            errors.append("OrderItem: uniprice am")

        order_id = item["order_id"]
        line_total = item["uniprice"] * item["quantity"]

        totals[order_id] = totals.get(
            order_id, Decimal("0.00")
        ) + line_total

    # Kiem tra Order
    orders_by_id = {
        order["order_id"]: order
        for order in orders
    }

    for order in orders:
        customer_id_number = int(
        order["customer_id"].replace("CUST", "")
    )

        if not (1 <= customer_id_number <= COUNTS["Customer"]):
            errors.append("Order: customer_id khong ton tai")

        if order["store_id"] not in store_ids:
            errors.append("Order: store_id khong ton tai")

        if order["status"] not in {
            "pending", "completed", "canceled"
        }:
            errors.append("Order: status khong hop le")

        calculated = money(
            totals.get(order["order_id"], Decimal("0.00"))
        )

        if calculated != order["total_amount"]:
            errors.append(
                f"Order {order['order_id']}: total_amount sai"
            )

    # Kiem tra Payment
    for payment in payments:
        order = orders_by_id.get(payment["order_id"])

        if order is None:
            errors.append("Payment: order_id khong ton tai")

        elif order["status"] != "completed":
            errors.append(
                f"Payment {payment['payment_id']}: "
                "Order chua completed"
            )

    if errors:
        for error in errors[:20]:
            print("-", error)

        raise ValueError("Batch co du lieu khong hop le.")


#9. XUAT DU LIEU
if __name__ == "__main__":

    # 1. Sinh cac bang danh muc
    categories = generate_categories()
    stores = generate_stores()
    products = generate_products(categories)

    # 2. Tao tap hop ID de kiem tra FK
    store_ids = {
        row["store_id"] for row in stores
    }
    product_ids = {
        row["product_id"] for row in products
    }

    # 3. Khoi tao file cho cac bang danh muc
    exports = {}

    master_tables = {
        "Category": categories,
        "Store": stores,
        "Product": products,
    }

    for table_name, rows in master_tables.items():
        exports[table_name] = initialize_export(
            table_name,
            list(rows[0].keys())
        )
        append_export(exports[table_name], rows)

    # 4. Khoi tao file cho cac bang giao dich
    exports["Order"] = initialize_export(
        "Order",
        [
            "order_id", "customer_id", "store_id",
            "order_date", "status", "total_amount"
        ]
    )

    exports["OrderItem"] = initialize_export(
        "OrderItem",
        [
            "order_item_id", "order_id", "product_id",
            "quantity", "uniprice"
        ]
    )

    exports["Payment"] = initialize_export(
        "Payment",
        [
            "payment_id", "order_id", "payment_date",
            "amount", "payment_method"
        ]
    )

    exports["Customer"] = initialize_export(
        "Customer",
        ["customer_id", "name", "email", "phone_number"]
    )

    for customers_batch in generate_customers():
        append_export(exports["Customer"], customers_batch)

    # 5. Sinh va xu ly tung batch
    payment_number = 0

    for orders_batch, items_batch in generate_orders(
        stores, products
    ):

        payments_batch = []

        for order in orders_batch:
            order_number = int(
                order["order_id"].replace("ORD", "")
            )

            # Chi Order completed moi co Payment
            if order_number <= COMPLETED_COUNT:

                is_paid = (
                    order_number * COUNTS["Payment"]
                    // COMPLETED_COUNT
                    >
                    (order_number - 1) * COUNTS["Payment"]
                    // COMPLETED_COUNT
                )

                if is_paid:
                    payment_number += 1

                    payments_batch.append(
                        create_payment(order, payment_number)
                    )

        # 6. Kiem tra batch
        validate_batch(
            orders_batch,
            items_batch,
            payments_batch,
            store_ids,
            product_ids
        )

        # 7. Xuat batch vao cac file
        append_export(exports["Order"], orders_batch)
        append_export(exports["OrderItem"], items_batch)
        append_export(exports["Payment"], payments_batch)

        print(
            f"Da xu ly {exports['Order']['count']:,} "
            f"/ {ORDER_COUNT:,} Orders"
        )

    # 8. Hoan tat cac file
    for export_info in exports.values():
        finalize_export(export_info)

    # 9. Kiem tra tong so ban ghi
    actual_total = sum(
        export_info["count"]
        for export_info in exports.values()
    )

    expected_total = sum(COUNTS.values())

    if actual_total != expected_total:
        raise ValueError(
            f"Tong ban ghi sai: {actual_total}, "
            f"mong doi {expected_total}"
        )

    if payment_number != COUNTS["Payment"]:
        raise ValueError("So luong Payment khong dung")

    print("\nHOAN TAT!")
    print("Tong so ban ghi:", actual_total)
    print("Thu muc ket qua:", OUTPUT_DIR.resolve())
