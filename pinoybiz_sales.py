import sqlite3
import datetime
from time import time

DATABASE_NAME = "PinoyBiz_sales.db"
current_date = datetime.datetime.now().date()

def calculate_discount(amount, addtional_discount):
    initial_discount = 0
    other_discount = 0
    if amount >= 1000:
        initial_discount = amount * .1
    if addtional_discount == 1:
        other_discount = (amount - initial_discount) * .05
    return initial_discount + other_discount

def create_table(query):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def add_customer():
    name = input("Name: ")
    email = input("Email: ")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    cursor.close()
    conn.close()
    
def add_product():
    product = input("Product: ")
    price = input("Price: ")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (product, price) VALUES (?, ?)", (product, price))
    conn.commit()
    cursor.close()
    conn.close()
    
def add_orders():
    customer = input("Customer (ID): ")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    conn.execute("Begin")
    try:
        cursor.execute("INSERT INTO orders (customer_id, created_at, updated_at) VALUES (?, DATE('now'), DATE('now'))", (customer,))
        conn.commit()
        last_inserted_order_id = cursor.lastrowid
        product = int(input("Product (ID): "))
        quantity = int(input("Quantity: "))
        cursor.execute("INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)", (last_inserted_order_id, product, quantity))
        conn.execute("COMMIT")
    except sqlite3.Error as e:
        conn.execute("ROLLBACK")
        print(f"Error: {e}")
    cursor.close()
    conn.close()
    
def view_customers():
    try:
        print("Customers: ")
        conn = sqlite3.connect(DATABASE_NAME)
        conn.create_function("calculate_discount", 2, calculate_discount)
        cursor = conn.cursor()
        cursor.execute("""SELECT 
                        customers.id
                        ,customers.name
                        ,customers.email
                        ,(
                            SELECT SUM(
                                prod.price * od.quantity - 
                                calculate_discount(prod.price * od.quantity, 
                                    (SELECT EXISTS ( 
                                        SELECT 1 
                                        FROM orders as discOrder 
                                        WHERE discOrder.id < o.id 
                                            AND discOrder.customer_id = customers.id 
                                            AND discOrder.created_at BETWEEN DATE(o.created_at, '-30 days') AND o.created_at
                                        LIMIT 1 
                                    ))
                                )
                            )
                            FROM order_details as od
                            LEFT JOIN products as prod ON od.product_id = prod.id
                            LEFT JOIN orders as o ON od.order_id = o.id
                            WHERE o.customer_id = customers.id
                        )
                    FROM customers
                    """)
        rows = cursor.fetchall()
        row_header = f"{'ID':<4} | {'Name':<15} | {'Email':<20} | {'Total Amount':<20}"
        print(row_header)
        print(len(row_header) * "-")
        for row in rows:
            (row_id, row_name, row_email, row_amount) = row
            print(f"{row_id:<4} | {row_name:<15} | {row_email:<20} | {row_amount if row_amount != None else '':<20} ")
        print("\n")
    except sqlite3.Error as e:
           print(f"Error: {e}")

def view_products():
    try:
        print("Products: ")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, product, price FROM products")
        rows = cursor.fetchall()
        row_header = f"{'ID':<4} | {'Product':<15} | {'Price':<20}"
        print(row_header)
        print(len(row_header) * "-")
        for row in rows:
            (row_id, row_product, row_price) = row
            print(f"{row_id:<4} | {row_product:<15} | {row_price:<20}")
        print("\n")
    except sqlite3.Error as e:
        print(f"Error: {e}")


        
    
def view_orders():
    try:
        print("Orders:")
        start_time = time()
        conn = sqlite3.connect(DATABASE_NAME)
        conn.create_function("calculate_discount", 2, calculate_discount)
        cursor = conn.cursor()
        cursor.execute(""" SELECT 
                            orders.ID
                            ,customers.name
                            ,orders.created_at
                            ,(
                            SELECT SUM(
                                prod.price * od.quantity - 
                                calculate_discount(prod.price * od.quantity, 
                                    (SELECT EXISTS ( 
                                        SELECT 1 
                                        FROM orders as discOrder 
                                        WHERE discOrder.id < o.id 
                                            AND discOrder.customer_id = customers.id 
                                            AND discOrder.created_at BETWEEN DATE(o.created_at, '-30 days') AND o.created_at
                                        LIMIT 1 
                                    ))
                                )
                            )
                            FROM order_details as od
                            LEFT JOIN products as prod ON od.product_id = prod.id
                            LEFT JOIN orders as o ON od.order_id = o.id
                            WHERE od.order_id = orders.ID
                        )
                        FROM orders
                        LEFT JOIN customers ON orders.customer_id = customers.id
                    """)
        rows = cursor.fetchall()
        row_header = f"{'ID':<4} | {'Customer':<15} | {'Order Date':<20} | {'Total Amount':<20}"
        print(row_header)
        print(len(row_header) * "-")
        for row in rows:
            (row_id, row_customer, row_date, row_amount) = row
            print(f"{row_id:<4} | {row_customer:<15} | {row_date:<20} | {row_amount:<20}")
        print(f"Rows Return in {time() - start_time} second(s)") 
        print("\n")
        # result without indexing 0.0010008811950683594
        # result after indexing 0.007892370223999023
    except sqlite3.Error as e:
        print(f"Error: {e}")

def view_order_details():
    try:
        print("Order Details:")
        conn = sqlite3.connect(DATABASE_NAME)
        conn.create_function("calculate_discount", 2, calculate_discount)
        cursor = conn.cursor()
        
        cursor.execute(""" SELECT order_details.id
                            ,products.product
                            ,products.price
                            ,order_details.quantity
                            ,(products.price * order_details.quantity)
                            ,calculate_discount(products.price * order_details.quantity, (SELECT EXISTS 
                                (
                                SELECT 1 FROM orders as o
                                WHERE o.id < orders.id AND o.customer_id = orders.customer_id AND o.created_at BETWEEN DATE(orders.created_at, '-30 days') AND orders.created_at
                                LIMIT 1
                                )))
                            ,(products.price * order_details.quantity) - calculate_discount(products.price * order_details.quantity, (SELECT EXISTS 
                                (
                                SELECT 1 FROM orders as o
                                WHERE o.id < orders.id AND o.customer_id = orders.customer_id AND o.created_at BETWEEN DATE(orders.created_at, '-30 days') AND orders.created_at
                                LIMIT 1
                                )))
                            ,orders.created_at
                            ,orders.customer_id
                            ,orders.id
                        FROM order_details
                        LEFT JOIN products on order_details.product_id = products.id
                        LEFT JOIN orders on order_details.order_id = orders.id
                    """)
        rows = cursor.fetchall()
        row_header = f"{'ID':<4} | {'Product':<20} | {'Price':<10} | {'Quantity':<10} | {'Amount':<20} | {'Discount':<20} | {'Total':<20}"
        print(row_header)
        print(len(row_header) * "-")
        for row in rows:
            (row_id, row_product, row_price, row_qty, row_amount, row_discount , row_total_amount, row_order_date, row_customer_id, row_order_id) = row
            print(f"{row_id:<4} | {row_product:<20} | {row_price:<10} | {row_qty:<10} | {row_amount if row_amount != None else '':<20} | {row_discount:<20} | {row_total_amount:<20}")
        print("\n")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    
def create_index(index_name, table, column):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.executeq(f"CREATE INDEX {index_name} ON {table}({column})")

def create_trigger():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TRIGGER update_date 
                    AFTER INSERT ON order_details
                    FOR EACH ROW
                    BEGIN
                        UPDATE orders SET updated_at = DATE('now') WHERE id = NEW.order_id;
                    END;
                    """)

customer_table_query = """
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY
        ,name TEXT
        ,email TEXT
    )
"""

products_table_query = """
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY
        ,product TEXT
        ,price INTEGER
    )
"""

orders_table_query = """
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY
        ,customer_id TEXT
        ,created_at DATE
        ,updated_at DATE
    )
"""

order_details_table_query = """
    CREATE TABLE IF NOT EXISTS order_details(
        id INTEGER PRIMARY KEY
        ,order_id INTEGER
        ,product_id INTEGER
        ,quantity INTEGER
        ,created_at DATE
    )
"""

table_queries = [customer_table_query, products_table_query, orders_table_query, order_details_table_query]

for query in table_queries:
    create_table(query)

view_customers()
view_products()
view_orders()
view_order_details()
menu_input = int(input("Enter 1: Add Customer, 2: Add Products, 3: Add Order: "))
if menu_input == 1:
    add_customer()
    view_customers()
elif menu_input == 2:
    add_product()
    view_products()
elif menu_input == 3:
    add_orders()



