import sqlite3
import os
import platform

message = """
1. Show products list
2. Add a new product
3. Delete a product
4. Edit product
5. Sell a product
6. Exit
"""

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "products.db")

def get_db_connection():
    return sqlite3.connect(db_path)

def init_database():
    with get_db_connection() as db:
        cr = db.cursor()
        cr.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                product_price REAL,
                product_quantity INTEGER
            )
        """)
        db.commit()

def print_product_details(product):
    print(f"ID: {product[0]}")
    print(f"Name: {product[1]}")
    print(f"Price: {product[2]} EGP")
    print(f"Quantity: {product[3]}")

def get_product_fields(product_id):
    try:
        product_id = int(product_id)
    except ValueError:
        print("Please enter a valid product ID (number)")
        input("\nPress Enter to continue...")
        return False
    with get_db_connection() as db:
        cr = db.cursor()
        try:
            cr.execute("SELECT * FROM products WHERE product_id = ?", (product_id, ))
            results = cr.fetchall()
            if not results:
                print("Cannot find a product with this id")
                input("\nPress Enter to continue...")
                return False
            for row in results:
                print_product_details(row)
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to continue...")
            return False
        except Exception as e:
            print(f"Error: {e}")
            input("\nPress Enter to continue...")
            return False

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def prompt_input(prompt, cast_type=None, allow_empty=False, positive_only=False):
    while True:
        value = input(prompt)
        if not value and allow_empty:
            return value
        if not value:
            print("Input cannot be empty!")
            continue
        if cast_type:
            try:
                value_casted = cast_type(value)
                if positive_only and value_casted < 0:
                    print("Please enter a positive value!")
                    continue
                return value_casted
            except ValueError:
                print(f"Please enter a valid {cast_type.__name__}!")
        else:
            return value

def show_products_list():
    clear_screen()
    print("Products List:\n")
    print(
        "Product Name".ljust(25) +
        "Price".ljust(12) +
        "Quantity".ljust(12) +
        "Product ID".ljust(10)
    )
    print("-" * 60)
    with get_db_connection() as db:
        cr = db.cursor()
        try:
            cr.execute("SELECT * FROM products")
            products = cr.fetchall()
            if not products:
                print("No products found")
            else:
                for product in products:
                    name = product[1][:24].ljust(25)
                    price = str(product[2]).ljust(12)
                    quantity = str(product[3]).ljust(12)
                    product_id = str(product[0]).zfill(4).ljust(10)
                    print(name + price + quantity + product_id)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    print("-" * 60)
    search = input("\nSearch for a product OR Press Enter to continue...")
    if search == "":
        return
    clear_screen()
    with get_db_connection() as db:
        cr = db.cursor()
        query = "SELECT * FROM products WHERE product_name LIKE ?"
        cr.execute(query, ('%' + search + '%',))
        results = cr.fetchall()
        if results:
            print("\nProducts Found:")
            print("-" * 60)
            print(
                "Product Name".ljust(25) +
                "Price".ljust(12) +
                "Quantity".ljust(12) +
                "Product ID".ljust(10)
            )
            print("-" * 60)
            for product in results:
                name = product[1].ljust(25)
                price = str(product[2]).ljust(12)
                quantity = str(product[3]).ljust(12)
                product_id = str(product[0]).zfill(4).ljust(10)
                print(name + price + quantity + product_id)
            input("\nPress Enter to continue...")
        else:
            print("No products with this name.")
            input("\nPress Enter to continue...")

def add_product():
    clear_screen()
    print(" Add Product ".center(80, "#"))
    name = prompt_input("\nWrite the product name: ")
    price = prompt_input("Write the product price: ", float, positive_only=True)
    quantity = prompt_input("Write the product quantity: ", int, positive_only=True)
    with get_db_connection() as db:
        cr = db.cursor()
        cr.execute("INSERT INTO products (product_name, product_price, product_quantity) VALUES(?, ?, ?)", (name, price, quantity))
        db.commit()
    print("Product added successfully!")
    input("\nPress Enter to continue...")

def delete_product():
    clear_screen()
    print("Delete Product".center(100, "#"))
    product_id = prompt_input("Write the product id: ", int)
    with get_db_connection() as db:
        cr = db.cursor()
        try:
            cr.execute("SELECT * FROM products WHERE product_id = ?", (product_id, ))
            results = cr.fetchall()
            if not results:
                print("Cannot find a product with this id")
                input("\nPress Enter to continue...")
                return False
            print("Product Details:")
            print("-" * 30)
            for row in results:
                print_product_details(row)
            confirm = input("\nAre you sure you want to delete this product? (y/n): ")
            if confirm.lower() in ['y', 'yes']:
                cr.execute("DELETE FROM products WHERE product_id = ?" , (product_id, ))
                db.commit()
                print("Product deleted successfully!")
            else:
                print("Deletion cancelled.")
            input("\nPress Enter to continue...")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to continue...")
            return False
        except Exception as e:
            print(f"Error: {e}")
            input("\nPress Enter to continue...")
            return False

def edit_product():
    clear_screen()
    print("Edit Product".center(100, "#"))
    product_id = prompt_input("Write the product id: ", int)
    if not get_product_fields(product_id):
        return
    print("Click Enter if you don't want to change this field".center(100, "="))
    changes_made = False
    product_name_input = prompt_input("Write the product name: ", allow_empty=True)
    with get_db_connection() as db:
        cr = db.cursor()
        if product_name_input != "":
            cr.execute("UPDATE products SET product_name = ? WHERE product_id = ?", (product_name_input, product_id))
            changes_made = True
        product_price_input = prompt_input("Write the product price: ", float, allow_empty=True, positive_only=True)
        if product_price_input != "":
            cr.execute("UPDATE products SET product_price = ? WHERE product_id = ?", (product_price_input, product_id))
            changes_made = True
        product_quantity_input = prompt_input("Write the product quantity: ", int, allow_empty=True, positive_only=True)
        if product_quantity_input != "":
            cr.execute("UPDATE products SET product_quantity = ? WHERE product_id = ?", (product_quantity_input, product_id))
            changes_made = True
        if changes_made:
            confirm = input("\nDo you want to save these changes? (y/n): ")
            if confirm.lower() in ['y', 'yes']:
                db.commit()
                print("Product updated successfully!")
            else:
                print("Changes cancelled.")
        else:
            print("No changes were made.")
        input("\nPress Enter to continue...")

def sell_product():
    clear_screen()
    print("Sell Product".center(100, "#"))
    product_id = prompt_input("Write the product id: ", int)
    if not get_product_fields(product_id):
        print("Cannot find product with this id.")
        input("\nPress Enter to continue...")
        return False
    with get_db_connection() as db:
        cr = db.cursor()
        try:
            while True:
                quantity_input = prompt_input("\nWrite the quantity: ", int, positive_only=True)
                cr.execute("SELECT product_quantity, product_price FROM products WHERE product_id = ?", (product_id, ))
                result = cr.fetchone()
                if not result:
                    print("Product not found. It may have been deleted.")
                    input("\nPress Enter to continue...")
                    return False
                quantity, price = result
                remaining_quantity = quantity - quantity_input
                if remaining_quantity < 0:
                    print(f"There is not enough quantity. Available: {quantity}")
                    continue
                cost = price * quantity_input
                print("\nCost: ", str(cost))
                if remaining_quantity == 0:
                    cr.execute("DELETE FROM products WHERE product_id = ?", (product_id, ))
                    db.commit()
                    print("The product has expired.")
                else:
                    cr.execute("UPDATE products SET product_quantity = ? WHERE product_id = ?", (remaining_quantity, product_id))
                    db.commit()
                    print("The remaining quantity is ", remaining_quantity)
                input("\nPress Enter to continue...")
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to continue...")
            return False
        except Exception as e:
            print("Error: ", e)
            input("\nPress Enter to continue...")
            return False

def main():
    init_database()
    while True:
        clear_screen()
        print(message)
        choice = input("Enter your choice: ").strip()
        if choice == "1" or choice.lower() == "show products list":
            show_products_list()
        elif choice == "2" or choice.lower() == "add product":
            add_product()
        elif choice == "3" or choice.lower() == "delete product":
            delete_product()
        elif choice == "4" or choice.lower() == "edit product":
            edit_product()
        elif choice == "5" or choice.lower() == "sell product":
            sell_product()
        elif choice == "6" or choice.lower() == "exit":
            clear_screen()
            print("Thank you for using the Inventory Management System!")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()