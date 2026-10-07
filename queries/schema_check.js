db = db.getSiblingDB("sales_test");
db.orders.drop();
db.orders.insertMany([
  {order_id: 1, customer_id: 10001, store_id: 15, order_date: new Date("2026-03-15T08:30:00Z"),
   status: "Completed", items: [{product_id: 1001, category_id: 5, quantity: 2, unit_price: 150000}], total_amount: 300000},
  {order_id: 2, customer_id: 10002, store_id: 15, order_date: new Date("2026-03-20T10:00:00Z"),
   status: "Completed", items: [{product_id: 1001, category_id: 5, quantity: 1, unit_price: 150000},
                               {product_id: 1002, category_id: 6, quantity: 3, unit_price: 50000}], total_amount: 300000},
  {order_id: 3, customer_id: 10001, store_id: 16, order_date: new Date("2026-04-02T09:00:00Z"),
   status: "Cancelled", items: [{product_id: 1002, category_id: 6, quantity: 1, unit_price: 50000}], total_amount: 50000}
]);
print("count = " + db.orders.countDocuments());
print("--- revenue by month (Completed only) ---");
printjson(db.orders.aggregate([
  {$match: {status: "Completed"}},
  {$group: {_id: {$dateToString: {format: "%Y-%m", date: "$order_date"}}, revenue: {$sum: "$total_amount"}}},
  {$sort: {_id: 1}}
]).toArray());
print("--- revenue by category (all statuses) ---");
printjson(db.orders.aggregate([
  {$unwind: "$items"},
  {$group: {_id: "$items.category_id", revenue: {$sum: {$multiply: ["$items.quantity", "$items.unit_price"]}}}},
  {$sort: {_id: 1}}
]).toArray());
