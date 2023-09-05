import tkinter as tk
from tkinter import ttk
from tkinter import *
from datetime import datetime
import os,tempfile
import win32print
import win32ui
from tabulate import tabulate
from fpdf import FPDF
import time
from datetime import date
import random
from tkinter.simpledialog import askinteger
from tkinter import simpledialog,filedialog
import sqlite3
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import subprocess
import tkinter as tk
from tkinter import ttk


current_table=1

canceled_kots={}
stored_bill_text = ""
global billNo
billNo = str(random.randint(1, 10000))
previous_table = None

def remove_steward_selection(table):
    if table in steward_selections:
        del steward_selections[table]
    billNo = str(random.randint(1, 10000))
    table_bill_numbers[current_table] = billNo
        

def take_order(table_number):
    global current_table,previous_table
    
    current_table = table_number

    # Get the selected steward for the current table
    steward_value = get_steward_selection(current_table)

    # Update the steward dropdown to the selected steward for this table
    steward_dropdown.set(steward_value)
    mode_dropdown.set("Dine In")

    # Update the order label with the table number and steward name
    order_label.config(text=f"Taking order for Table {table_number}:\n Steward: {steward_value}")
    if current_table != previous_table:
        switch_table(current_table)

    update_order_label(current_table)
    update_removed_items_label()
    previous_table = current_table
    

def take_away_order(order_type):
    global current_table,previous_table
    
    current_table = f" ({order_type})"
    steward_value = get_steward_selection(current_table)

    # Update the steward dropdown to the selected steward for this table
    steward_dropdown.set(steward_value)
    mode_dropdown.set("Take Away")

    # Update the order label with the table number and steward name
    order_label.config(text=f"Taking order{order_type}:\n Steward: {steward_value}")
    if current_table != previous_table:
        switch_table(current_table)
    update_order_label(current_table)
    update_removed_items_label()
    previous_table = current_table


def planter_order(order_type):
    global current_table,previous_table
    current_table = f" ({order_type})"
    steward_value = get_steward_selection(current_table)

    # Update the steward dropdown to the selected steward for this table
    steward_dropdown.set(steward_value)
    mode_dropdown.set("Dine In")

    # Update the order label with the table number and steward name
    order_label.config(text=f"Taking order{order_type}:\n Steward: {steward_value}")
    if current_table != previous_table:
        switch_table(current_table)
    update_order_label(current_table)
    update_removed_items_label()
    previous_table = current_table


def display_category_food(category):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM food WHERE category = ?', (category,))
    food_items = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    food_listbox.delete(0, tk.END)
    for item in food_items:
        food_listbox.insert(tk.END, item)

steward_selections = {}

# Function to set the steward selection for the current table
def set_steward_selection(current_table, steward):
    steward_selections[current_table] = steward
    print(steward_selections)

# Function to get the steward selection for the current table
def get_steward_selection(current_table):
    return steward_selections.get(current_table, "")


def update_order_label(current_table):
    steward_value = get_steward_selection(current_table)  # Get the selected steward for the table
    if not steward_value:
        steward_value = steward_dropdown.get()  # Get the default steward from the dropdown if not set
        set_steward_selection(current_table, steward_value)  # Set the steward for this table
    order_text = f"Taking order for\n Table{current_table}:\n Steward: {steward_value}\n"
    selected_food = table_orders.get(current_table, [])
    order_total = 0
    
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    for item in selected_food:
        cursor.execute('SELECT price FROM food WHERE name = ?', (item,))    
        row = cursor.fetchone()
        order_text += f"{item} x {selected_food[item]}\n"

    conn.close()
    
    order_label.config(text=order_text)




    

#def update_listbox(event):
 #   query = search_entry.get().strip().lower()
  #  food_listbox.delete(0, tk.END)
    
   # for items in category_food_map.values():
    #    for item in items:
     #       if query and item.lower().startswith(query):
      #          food_listbox.insert(tk.END, item)


def update_listbox(event):
    query = search_entry.get().strip().lower()
    food_listbox.delete(0, tk.END)
    
    if not query:  # If the search query is empty, fetch and display all food items
        conn = sqlite3.connect('food_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT name FROM food')
        food_items = cursor.fetchall()

        for item in food_items:
            food_listbox.insert(tk.END, item[0])

        conn.close()
    else:
        # Fetch and display food items based on the search query
        conn = sqlite3.connect('food_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT name FROM food WHERE LOWER(name) LIKE ?', (f'{query}%',))
        food_items = cursor.fetchall()

        for item in food_items:
            food_listbox.insert(tk.END, item[0])

        conn.close()



def on_listbox_select(event):
    global selected_items
    selected_items = food_listbox.curselection()
    update_order_label(current_table)  # Update the order label when selections are made

def add_to_order(steward_name):
    selected_food = table_orders.setdefault(current_table, {})
    
    for index in selected_items:
        item = food_listbox.get(index)
        selected_food[item] = selected_food.get(item, 0) + 1

    # Store the steward name for the current table
    set_steward_selection(current_table, steward_name)
    
    '''if not current_steward:
        # Steward not set for this table, set it to the selected steward
        set_steward_selection(current_table, steward_name)
        # Update the order label with the current table and steward name
        update_order_label(current_table)
    else:
        # Steward is already set, do not allow changing it
        print("Steward is already set for this table:", current_steward)
    '''
    # Update the order label with the current table and steward name
    update_order_label(current_table)


def remove_from_order():
    selected_food = table_orders.get(current_table, {})
    
    for index in selected_items:
        item = food_listbox.get(index)
        if item in selected_food and selected_food[item] > 0:
            selected_food[item] -= 1
            if selected_food[item] == 0:
                del selected_food[item]
    
    update_order_label(current_table)




table_bills = {}

def generate_bill(current_table, mode_of_payment=None):
    global bill_total, item, stored_bill_text, billNo
    total_amount = 0
    today = str(date.today())
    if current_table not in table_bill_numbers:
        billNo = str(random.randint(1, 10000))
        table_bill_numbers[current_table] = billNo
    else:
        billNo = table_bill_numbers[current_table]
    print(billNo)

    generate = "   THE MELTING POT BISTRO\n" + "        " + "Big Will Mart,\n" + "        " + "SDB Giri Road,\n" + "         " + "Kalimpong.\n" + "          " + mode_dropdown.get() + "\nBill No:Bill " + billNo + " " + today + "\n-----------------------------------\nMode of Payment:" + payment_dropdown.get() + "\n-----------------------------------\n"

    # Define the column widths
    item_width = 18
    qty_x = 2 # X position for quantity (common for all)
    rate_x = 12 # X position for rate

    bill_text = generate + f"Bill for Table- {current_table}:\n-----------------------------------\n"
    bill_text += f"{'Item'.ljust(item_width)}{'Qty'.rjust(qty_x - len('Item'))}{'Rate'.rjust(rate_x - qty_x - len('Qty'))}\n"  # Header row
    selected_food = table_orders.get(current_table, {})
    bill_total = 0

    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    for item in selected_food:
        quantity = selected_food[item]
        cursor.execute('SELECT price FROM food WHERE name = ?', (item,))
        row = cursor.fetchone()
        if row:
            price = row[0]
            item_total = quantity * price

            # Truncate or pad the item name to fit the column width
            formatted_item = (item[:item_width - 3] + '...') if len(item) > item_width else item

            # Format the quantity and rate with fixed X positions
            formatted_quantity = f"{quantity}".rjust(qty_x - len('Qty'))
            formatted_item_total = f"{' ' * 5}{item_total:.2f}".rjust(rate_x - len('Rate'))

            # Store the item details in the bill text
            bill_text += f"{formatted_item.ljust(item_width)}{formatted_quantity}{formatted_item_total}\n"
            bill_total += item_total

    conn.close()

    # Calculate the total bill amount
    total_bill_amount = bill_total
    
    # Calculate SGST (2.5% of the total amount)
    sgst_amount = total_bill_amount * 0.025
    cgst_amount = total_bill_amount * 0.025
    print(mode_of_payment)
    # Use the provided mode_of_payment if it's not None
    if mode_of_payment is not None:
        # Update the bill text to include the mode of payment
        if mode_of_payment == "NC":
            total_bill_amount = "NC"
            
                # Replace the mode of payment text
            #bill_text = bill_text.replace("Mode of Payment:", f"Mode of Payment: {mode_of_payment}\n", 1)

            #bill_text += f"{'Total'.ljust(item_width)}{''.rjust(qty_x +4)}{total_bill_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('Total')) + "\n"
            bill_text += f"{'S GST(2.5%)='.rjust(item_width+6)}{''.ljust(qty_x - len('Qty'))}{sgst_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('S GST')) + "\n"
            bill_text += f"{'C GST(2.5%)='.rjust(item_width+6)}{''.ljust(qty_x - len('Qty'))}{cgst_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('C GST')) + "\n"
            bill_text += f"{'Final Amount'.ljust(item_width)}{'NC'.rjust(qty_x + 6)}"

            bill_text += f"\n{'  Thank You...  Visit Again!'}"
            bill_text += f"\n\t{'  Powered by '}"
            bill_text += f"\n{'  PixelBridge Technologies.'}"
            save_bill(bill_text,current_table,billNo)
            if current_table in table_bills:
                del table_bills[current_table]
            payment_dropdown.set("")

            update_order_label(current_table)

            clear_order_for_table(current_table)
            remove_steward_selection(current_table)
            bill_text_area.delete("1.0", "end")
            bill_total = 0
        
            
        else:
                # Update the bill text to include the mode of payment and total amount
            #bill_text = bill_text.replace("Mode of Payment:", f"Mode of Payment: {mode_of_payment}\n",1)

        # Check if the mode_of_payment is "NC" and set total_amount to "NC"
        #if mode_of_payment == "NC":
            

        # Add SGST details to the bill
            bill_text += f"{'Total'.ljust(item_width)}{''.rjust(qty_x +4)}{total_bill_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('Total')) + "\n"
            bill_text += f"{'S GST(2.5%)='.rjust(item_width+6)}{''.ljust(qty_x - len('Qty'))}{sgst_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('S GST')) + "\n"
            bill_text += f"{'C GST(2.5%)='.rjust(item_width+6)}{''.ljust(qty_x - len('Qty'))}{cgst_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('C GST')) + "\n"
            bill_text += f"{'Final Amount'.ljust(item_width)}{''.rjust(qty_x +4)}{total_bill_amount:.2f}".rjust(rate_x - qty_x - len('Qty') - len('Total')) + "\n"
            bill_text += f"\n{'  Thank You...  Visit Again!'}"
            bill_text += f"\n\t{'  Powered by '}"
            bill_text += f"\n{'  PixelBridge Technologies.'}"

            bill_text_area.delete("1.0", "end")  # Clear the text area
            bill_text_area.insert("1.0", bill_text)


    canceled_kots[current_table] = []  # Clear canceled orders for the table
    total_amount = total_bill_amount
    stored_bill_text = bill_text_area.get("1.0", "end")
    print(stored_bill_text)

    table_bills[current_table] = {
        "text": bill_text,
        'total': total_amount,
    }

    # Print the bill text directly from the text area
    printer_name = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)
    lines = stored_bill_text.split('\n')  # Split the text into lines

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("Bill")
    hdc.StartPage()

    # Use a monospaced font like Courier New
    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 29,  # Increase the font size here
        "weight": 700,
    })
    hdc.SelectObject(font)

    line_height = 40  # Adjust this value based on line spacing
    y_position = 10  # Adjust this value to set the initial y position

    for line in lines:
        hdc.TextOut(100, y_position, line)
        y_position += line_height

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    win32print.ClosePrinter(hprinter)










'''def generate_bill(current_table, mode_of_payment=None):
    global bill_total, item, stored_bill_text,billNo
    total_amount = 0
    today = str(date.today())
    billNo = str(random.randint(1, 10000))
    generate = "THE MELTING POT BILL\n\tBig Will Mart,\n\tSDB Giri Road,\n\t\tKalimpong.\n" + "       " + mode_dropdown.get() + "\nReceipt No:  BIll " + billNo + "    " + today + "\n------------------\nMode of Payment:" + payment_dropdown.get() + "\n------------------\n"
    bill_text = generate + f"Bill for Table- {current_table}:\n------------------\nitem    qty    rate\n"
    selected_food = table_orders.get(current_table, {})
    stored_bill_text = bill_text
    print(selected_food)
    bill_total = 0

    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    for item in selected_food:
        quantity = selected_food[item]
        cursor.execute('SELECT price FROM food WHERE name = ?', (item,))
        row = cursor.fetchone()
        if row:
            price = row[0]
            item_total = quantity * price
            bill_text += f"{item}\n {quantity} {item_total:.2f}\n"
            bill_total += item_total

    conn.close()

    # Use the provided mode_of_payment if it's not None
    if mode_of_payment is not None:
        bill_text = bill_text.replace("Mode of Payment: No Charge (NC)", f"Mode of Payment: {mode_of_payment}")

    bill_label.config(text=bill_text, font=("times new roman", 12, "bold"))

    canceled_kots[current_table] = []  # Clear canceled orders for the table
    total_amount = bill_total
    stored_bill_text = bill_label.cget("text")

    file = tempfile.mktemp(".txt")
    open(file, "w").write(stored_bill_text)
    os.startfile(file, "print")'''

    

    



   
    


'''def clear_generate_bill():
    bill_label.config(text="BILLING SECTION",font=("helvetica",12,'bold'))
    removed_items_label.config(text="CANCELLED KOT'S",font=("helvetica",12,'bold'),justify='center')
    order_label.config(text="Taking order for :", font=('Helvetica', 14, 'bold'), fg='white',bg="#003535" ,justify='center')'''

def print_kot(current_table):
    steward_value = get_steward_selection(current_table)  # Get the selected steward for the current table
    order_text = order_label.cget("text")

    kot_text = f"{order_text}"

    # Define the column widths for formatting

    file = tempfile.mktemp(".txt")
    open(file, "w").write(kot_text)

    # Printing with font formatting
    printer_name = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("KOT")
    hdc.StartPage()

    # Use the same font settings as in generate_bill function
    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 22,  # Adjust the font size as needed
        "weight": 700,
    })
    hdc.SelectObject(font)

    line_height = 30
    y_position = 10

    lines = kot_text.split('\n')

    for line in lines:
        hdc.TextOut(100, y_position, line)
        y_position += line_height

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    win32print.ClosePrinter(hprinter)



      
def clear_order_for_table(table):
    order_label.config(text="Taking order for:")
    if table in table_orders:
        del table_orders[table]
        steward_dropdown.set("")

def print_bill():
   
    # Get the mode of payment
    mode_of_payment = payment_dropdown.get()

    # Generate the bill with the mode of payment and store the generated text
    generate_bill(current_table, mode_of_payment)

    # Print the stored bill text
    #printfinal(current_table)

      #bill_label.config(text="")

#creating db to insert bill of food sold
def insert_food_sales(food_items_with_prices):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    # Create the food sales table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_sales (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 0,
            total_price REAL DEFAULT 0
        )
    ''')

    # Insert food items from the bill into the food sales table
    for name, price in food_items_with_prices:
        cursor.execute('INSERT INTO food_sales (name, price) VALUES (?, ?)', (name, price))

    conn.commit()
    conn.close()

def update_or_insert_food_sales(food_items_with_data):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()
    
    for food_name, data in food_items_with_data.items():
        # Check if the food item with the same name exists in the database
        cursor.execute('SELECT id, quantity, total_price FROM food_sales WHERE name = ?', (food_name,))
        row = cursor.fetchone()
        
        if row:
            # Update existing food item
            item_id, existing_quantity, existing_total_price = row
            new_quantity = existing_quantity + data['quantity']
            new_total_price = existing_total_price + data['total_price']
            cursor.execute('UPDATE food_sales SET quantity = ?, total_price = ? WHERE id = ?', (new_quantity, new_total_price, item_id))
        else:
            # Insert new food item
            cursor.execute('INSERT INTO food_sales (name, quantity, total_price) VALUES (?, ?, ?)', (food_name, data['quantity'], data['total_price']))
    
    conn.commit()
    conn.close()


def printfinal(current_table):
    global bill_text_area, bill_total

    # Get the current bill text from the text area
    bill_text = bill_text_area.get("1.0", "end")

    '''food_items_with_data = {}
    lines = bill_text.split('\n')
    for line in lines:
        if line.strip().startswith('Item'):
            continue
        parts = line.split()
        if len(parts) >= 3:
            food_name = ' '.join(parts[:-2])  # Combine all parts except the last two (name of the food)
            try:
                quantity = int(parts[-2])  # Convert the penultimate part to an integer (quantity)
                food_price = float(parts[-1])  # Convert the last part to a float (price)

                if food_name in food_items_with_data:
                    # Update existing food item
                    existing_data = food_items_with_data[food_name]
                    existing_data['quantity'] += quantity
                    existing_data['total_price'] += (food_price * quantity)
                else:
                    # Add new food item
                    food_items_with_data[food_name] = {
                        'quantity': quantity,
                        'total_price': food_price * quantity
                    }
            except ValueError:
                # Handle the case where quantity or price cannot be converted to int or float
                print(f"Skipping invalid line: {line}")

    # Insert or update food items with names, prices, quantities, and total prices into the food sales table
    if food_items_with_data:
        insert_food_sales(food_items_with_prices)
        update_or_insert_food_sales(food_items_with_data)
        print(f"Updated or inserted food items wit''''''h names, prices, quantities, and total prices into the food sales table for Table {current_table}")'''



    # Get the mode of payment
    mode_of_payment = payment_dropdown.get()

    # Update the bill text to include the mode of payment
    updated_bill_text = bill_text.replace("Mode of Payment:", "Mode of Payment: %s" % mode_of_payment)

    # Calculate the total amount
    total_amount = bill_total
    total_amount_text = "Total Amount: %.2f" % total_amount
    billNo = table_bill_numbers.get(current_table, "")

    # Print the bill and total amount with the same billNo
    printer_name = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)
    lines = updated_bill_text.split('\n')  # Split the text into lines

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("Bill %s" % billNo)  # Use billNo in the document name
    hdc.StartPage()

    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 29,  # Increase the font size here
        "weight": 700,
    })
    hdc.SelectObject(font)

    line_height = 40  # Adjust this value based on line spacing
    y_position = 10  # Adjust this value to set the initial y position

    for line in lines:
        hdc.TextOut(100, y_position, line)
        y_position += line_height

    # Calculate and print the total amount
    total_amount_text = "Total Amount: %.2f" % total_amount
    total_amount_width = len(total_amount_text) * 15  # Adjust the width as needed
    total_amount_x = int((100 + 400 - total_amount_width) / 2)
    y_position += line_height  # Move to the next line

    hdc.TextOut(total_amount_x, y_position, total_amount_text)

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    win32print.ClosePrinter(hprinter)

    # Save the bill to a file with the same billNo as the file name
    save_bill(updated_bill_text, current_table, billNo)
    print(billNo)

    # Clear the bill from the dictionary for the current table
    if current_table in table_bills:
        del table_bills[current_table]

    # Clear the bill text area and reset the total amount
    bill_text_area.delete("1.0", "end")
    bill_total = 0

    payment_dropdown.set("")

    update_order_label(current_table)

    clear_order_for_table(current_table)
    remove_steward_selection(current_table)
    









def save_bill(bill_text, current_table, bill_number):
    if bill_text.strip():
        # Create the file name using the bill number
        file_name = f'Bill {bill_number}.txt'
        print(bill_number)

        # Define the default directory for saving bills
        default_directory = "C:/Users/USER/OneDrive/Desktop"  # Replace with your default directory

        # Ask the user for the save location
        file_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            initialfile=file_name,
            initialdir=default_directory,
            title='Save Bill'
        )

        if file_path:
            with open(file_path, 'w') as file:
                file.write(bill_text)
            messagebox.showinfo('Information', f'Bill {bill_number} Is Successfully Saved')
    else:
        messagebox.showwarning('Warning', 'There is no bill to save.')




table_bill_numbers = {}
def switch_table(current_table):
     global bill_text_area, bill_total

    # Clear the bill text area
     bill_text_area.delete("1.0", "end")

    # Check if there is a bill stored for the current table
     if current_table in table_bills:
        bill_info = table_bills[current_table]
        bill_text_area.insert("1.0", bill_info['text'])
        bill_total = bill_info['total']
     
     else:
        # Initialize bill_total to 0 if no bill is stored
        bill_total = 0
     if current_table in table_bill_numbers:
        billNo = table_bill_numbers[current_table]
     else:
        # If no bill number is stored, set a default value or generate a new bill number
        billNo = str(random.randint(1, 10000))
        table_bill_numbers[current_table] = billNo






      

      
      


def update_removed_items_label():
    removed_items_text = "CANCELLED KOT'S:\n\n"
    canceled_orders = canceled_kots.get(current_table, [])
    
    for canceled_order in canceled_orders:
        removed_items_text += f"Table {current_table}\nReason: {canceled_order['reason']}\nItems:\n"
        item_list = [f"{item} x {canceled_order['canceled_quantities'][item]}" for item in canceled_order['items']]
        removed_items_text += ', '.join(item_list) + "\n\n"
    
    removed_items_label.config(text=removed_items_text)

    # Printing with font formatting
    printer_name = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("Removed_Items")
    hdc.StartPage()

    # Use the same font settings as in print_kot function
    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 22,  # Adjust the font size as needed
        "weight": 700,
    })
    hdc.SelectObject(font)

    line_height = 30
    y_position = 10

    removed_items_lines = removed_items_text.split('\n')

    for line in removed_items_lines:
        hdc.TextOut(100, y_position, line)
        y_position += line_height

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    win32print.ClosePrinter(hprinter)

    
    

def ask_integer_quantity(item, max_quantity):
    quantity_to_cancel = askinteger(f"Cancel Quantity for {item}", f"Enter quantity to cancel for {item} (1-{max_quantity})", minvalue=1, maxvalue=max_quantity)
    return quantity_to_cancel

def cancel_kot():
    selected_item_indices = food_listbox.curselection()
    selected_food = table_orders.get(current_table, {})
    
    if selected_item_indices:
        reason = cancel_reason_var.get()  # Get the reason for cancellation
        if reason:
            canceled_quantities = {}  # Dictionary to store the quantity canceled for each item
            for index in selected_item_indices:
                item = food_listbox.get(index)
                if item in selected_food:
                    quantity_to_cancel = ask_integer_quantity(item, selected_food[item])
                    if quantity_to_cancel is not None and quantity_to_cancel > 0:
                        selected_food[item] -= quantity_to_cancel  # Decrement the quantity
                        if selected_food[item] == 0:
                            del selected_food[item]
                        canceled_quantities[item] = quantity_to_cancel
            
            if selected_food:
                table_orders[current_table] = selected_food  # Update the table orders
            else:
                del table_orders[current_table]  # Remove the table entry if no orders left
            
            canceled_orders = canceled_kots.get(current_table, [])
            canceled_orders.append({"items": list(canceled_quantities.keys()), "reason": reason, "canceled_quantities": canceled_quantities})
            canceled_kots[current_table] = canceled_orders
           
            
            update_order_label(current_table)  # Update the order label after canceling
            update_removed_items_label()  # Update the removed items label
        
        cancel_reason_var.set("")
        
        order_text = removed_items_label.cget("text")
      
        file=tempfile.mktemp(".txt")
        open(file,"w").write(order_text)
        os.startfile(file,"print")

def register():
    global first_name_entry,last_name_entry,num,dob,points
    global custLevel
    global search_num
    custLevel=Toplevel(bg="black")
    custLevel.geometry("500x500+100+100")
    title=Label(custLevel,text="CUSTOMER REGISTRATION FORM",bg="green",fg="white",font=("times new roman",20))
    title.pack(fill=X)
    search_cust=Label(custLevel,text="enter number to search",bg="black",fg="white",font=("times new roman",15))
    search_cust.place(x=20,y=80)
    search_num=Entry(custLevel,bg="white",fg="black",width=20,font=("times new roman",15))
    search_num.place(x=220,y=80)
           
    search_button=Button(custLevel,text="lookup",bg="green",fg="white",command=getData)
    search_button.place(x=390,y=80)

    diffFrame=Frame(custLevel,bg="grey",width=460,height=300)
    diffFrame.place(x=20,y=152)
           
    first_name=Label(diffFrame,text="FIRST NAME",bg="grey",fg="white",font=("times new roman",15),cursor="hand2")
    first_name.place(x=0,y=0)
    first_name_entry=Entry(diffFrame,bg="white",fg="black",width=20,font=("times new roman",15))
    first_name_entry.place(x=180,y=0)

    last_name=Label(diffFrame,text="LAST NAME",bg="grey",fg="white",font=("times new roman",15))
    last_name.place(x=0,y=50)
    last_name_entry=Entry(diffFrame,bg="white",fg="black",width=20,font=("times new roman",15))
    last_name_entry.place(x=180,y=50)

    num_label=Label(diffFrame,text="MOBILE NUMBER",bg="grey",fg="white",font=("times new roman",15))
    num_label.place(x=0,y=100)
    num=Entry(diffFrame,bg="white",fg="black",width=20,font=("times new roman",15))
    num.place(x=180,y=100)

    dob_label=Label(diffFrame,text="BIRTHDAY",bg="grey",fg="white",font=("times new roman",15))
    dob_label.place(x=0,y=150)
    dob=Entry(diffFrame,bg="white",fg="black",width=20,font=("times new roman",15))
    dob.place(x=180,y=150)
    dob.insert(0,"dd/mm/yy")

    points_label=Label(diffFrame,text="LOYALTY POINTS",bg="grey",fg="white",font=("times new roman",15))          
    points_label.place(x=0,y=200)
    points=Entry(diffFrame,bg="white",fg="black",width=20,font=("times new roman",15))
    points.place(x=180,y=200)

    save_button=Button(diffFrame,text="SAVE",bg="WHITE",fg="BLACK",width=10,command=sql)
    save_button.place(x=150,y=250)
           
    update_button=Button(diffFrame,text="UPDATE",bg="WHITE",fg="BLACK",width=10,command=updateDb)
    update_button.place(x=250,y=250)

def getData():
           first_name_entry.delete(0,END)
           last_name_entry.delete(0,END)
           num.delete(0,END)
           dob.delete(0,END)
           points.delete(0,END)
           

           conn=sqlite3.connect("custo.db")
           cur=conn.cursor()

           cur.execute('''SELECT * FROM custo''')
           val=cur.fetchall()

           for i in val:
            if(i[2]==search_num.get()):
               first_name_entry.insert(0,i[0])
               last_name_entry.insert(0,i[1])
               num.insert(0,i[2])
               dob.insert(0,i[3])
               points.insert(0,i[4])
           
           
           conn.commit()

           cur.close()
           conn.close()

def sql():
           tupl=[(first_name_entry.get(),last_name_entry.get(),num.get(),dob.get(),points.get())]
           conn=sqlite3.connect("custo.db")
           cur=conn.cursor()

           cur.execute('''CREATE TABLE IF NOT EXISTS custo(
                       first_name TEXT,last_name TEXT,number TEXT,birthday TEXT,points TEXT
           )''')

           cur.executemany('''INSERT INTO custo VALUES(?,?,?,?,?)''',tupl)

           first_name_entry.delete(0,END)
           last_name_entry.delete(0,END)
           num.delete(0,END)
           dob.delete(0,END)
           points.delete(0,END)

           messagebox.showinfo("information","customer registration completed!")

           custLevel.destroy()
           

           conn.commit()

           

           cur.close()
           conn.close()

def updateDb():
         fn = first_name_entry.get()
         ln = last_name_entry.get()
         nm = num.get()
         db = dob.get()
         pn = points.get()

         conn = sqlite3.connect("custo.db")
         cur = conn.cursor()

         update_query = "UPDATE custo SET first_name=?, last_name=?, birthday=?, points=? WHERE number=?"
         update_values = (fn, ln, db, pn, nm)

         cur.execute(update_query, update_values)
         conn.commit()

         messagebox.showinfo("Information", "Customer record updated successfully!")

         custLevel.destroy()

         cur.close()
         conn.close()




    
     


# Create root instance
root = tk.Tk()
root.title("THE MELTING POT BILLING | DEVELOPED BY PIXELBRIDGE TECHNOLOGIES")
root.geometry("1530x770+0+0")

month_var = tk.StringVar()
year_var = tk.StringVar()
# Create frame at the top for date display
date_frame = tk.Frame(root, bg='#003535')
date_frame.pack(side='top', fill='x')

# Get current date
current_date = date.today()

name_label = tk.Label(date_frame, text="THE MELTING POT BILLING", bg='#003535', padx=10,fg="white",font=("times new roman",20,"bold"))
name_label.pack(side='left')

# Create label for date display
date_label = tk.Label(date_frame, text=current_date, bg='#003535', padx=10,fg="white",font=("times new roman",20))
date_label.pack(side='right')

# Create left-side frame for menu categories
menu_frame = tk.Frame(root, bg='#003535')
menu_frame.pack(side='left', fill='y')

# Create label for menu
menu_label = tk.Label(menu_frame, text="Menu", bg='white',fg="#003535" ,padx=10, pady=10,font=("times new roman",20))
menu_label.pack(side='top',fill="x")

# Create buttons for menu categories
'''categories = ["Indian", "Continental", "Thai", "Italian", "Mexican", "Beverages", "Nepali"]

category_food_map = {
    "Indian": ["Butter Chicken", "Chicken Tikka"],
    "Continental": ["Grilled Chicken", "Pasta"],
    "Thai": ["Pad Thai", "Green Curry"],
    "Italian": ["Margherita Pizza", "Pasta Carbonara"],
    "Mexican": ["Tacos", "Burritos"],
    "Beverages": ["Virgin Mojito", "Coffee"],
    "Nepali": ["Momo", "Dal Bhat"]
}

food_price_map = {
    "Butter Chicken": 12.99,
    "Chicken Tikka": 9.99,
    "Grilled Chicken": 10.99,
    "Pasta": 8.99,
    "Pad Thai": 11.99,
    "Green Curry": 10.99,
    "Margherita Pizza": 14.99,
    "Pasta Carbonara": 13.99,
    "Tacos": 8.99,
    "Burritos": 9.99,
    "Virgin Mojito": 3.99,
    "Coffee": 2.99,
    "Momo": 7.99,
    "Dal Bhat": 6.99
}'''

table_orders = {}  # Dictionary to store orders for each table





# Create buttons for tables and place them horizontally
table_frame = tk.Frame(root, bg='#003535')
table_frame.pack(side='top', fill='x')

for i in range(1, 12):
    table_button = tk.Button(table_frame, text=f"Table {i}",bg="green",fg="white",font=("times new roman",15), command=lambda num=i: take_order(num))
    table_button.pack(side='left', padx=5, pady=5)

take_away_buttons_frame = tk.Frame(root, bg='#003535')
take_away_buttons_frame.pack(side='top', fill='x')

take_away_types = ["Take Away 1", "Take Away 2", "Take Away 3"]

for take_away_type in take_away_types:
    take_away_button = tk.Button(take_away_buttons_frame, text=take_away_type,bg="green",fg="white",font=("times new roman",15), command=lambda take_away=take_away_type: take_away_order(take_away))
    take_away_button.pack(side='left', padx=10, pady=5)

planters = ["Planter 1", "Planter 2", "Planter 3","Planter 4"]

for planter in planters:
    planter_button = tk.Button(take_away_buttons_frame, text=planter,bg="green",fg="white",font=("times new roman",15), command=lambda take_away=planter: planter_order(take_away))
    planter_button.pack(side='left', padx=10, pady=5)

# Create search input widget above the listbox
search_entry = tk.Entry(root,font=("times new roman",15))
search_entry.pack(side='top', padx=10, pady=10, fill='x')
search_entry.bind('<KeyRelease>', update_listbox)  # Bind the event to the callback function





####------trial basis of database------------###
def populate_food_listbox(selected_category=None):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    if selected_category:
        cursor.execute('SELECT name FROM food WHERE category = ?', (selected_category,))
    else:
        cursor.execute('SELECT name FROM food')

    food_items = [row[0] for row in cursor.fetchall()]

    food_listbox.delete(0, tk.END)  # Clear existing items from the Listbox

    for item in food_items:
        food_listbox.insert(tk.END, item)

    conn.close()



# Call the populate_food_listbox function when a category button is clicked
def display_category_food(category):
    populate_food_listbox(category)










# Create listbox for displaying food items
food_listbox = tk.Listbox(root,font=("times new roman",15))
food_listbox.pack(side='left', fill='both', expand=True)
food_listbox.bind('<<ListboxSelect>>', on_listbox_select)
 # Bind event to update function

# Populate listbox with all food items initially
'''for items in category_food_map.values():
    for item in items:
        food_listbox.insert(tk.END, item)'''

# Create frame on the right for food items and table buttons
right_frame = tk.Frame(root, bg='#003535')

right_frame.pack(side='right', fill='both', expand=False,pady=0)


steward_var=tk.StringVar()
steward_options=["manumit","babita","rohan",""]
steward_dropdown=ttk.Combobox(root,textvariable=steward_var,values=steward_options,font=("times new roman",15))
steward_dropdown.pack(side=TOP,padx=10,pady=5,fill="x")
# Create a button to add selected items to the order
add_button = tk.Button(root, text="Add to Order", command=lambda:add_to_order(steward_dropdown.get()),font=("times new roman",15),bg="green",fg="white")
add_button.pack(side='top', padx=10, pady=5, fill='x')

# Create label for order taking on the right side


remove_button = tk.Button(root, text="Remove", command=remove_from_order,font=("times new roman",15),bg="green",fg="white")
remove_button.pack(side='top', padx=10, pady=5, fill='x')

#generate_bill_button = tk.Button(root, text="Generate Bill", command=lambda:generate_bill(current_table),font=("times new roman",15),bg="green",fg="white")
#generate_bill_button.pack(side='top', padx=10, pady=5, fill='x')



# Create a frame for the bill



order_label = tk.Label(right_frame, text="Taking order for:", wraplength=180, font=('Helvetica', 12, 'bold'), fg='white',bg="#003535" ,justify='center')
order_label.pack(side='left', fill='y', padx=10, pady=0)

o_label = tk.Label(right_frame, text="",bg="white")
o_label.pack(side='left', fill='y', padx=10, pady=0)

#bill_label = tk.Label(right_frame, text="BILLING SECTION",font=('Helvetica', 12,'bold'),fg='white',bg="#003535", justify='left', anchor='center')
#bill_label.pack(side='right', fill='y', expand=True, padx=10, pady=0)
bill_text_area = Text(right_frame, wrap="word", width=35, height=20)
bill_text_area.pack(side="right",fill="y",padx=5,pady=0)


b_label = tk.Label(right_frame, text="",bg="white")
b_label.pack(side='right', fill='y', padx=10, pady=0)

removed_items_label = tk.Label(right_frame, text="CANCELLED KOT'S", wraplength=110,fg='white',bg="#003535",font=('Helvetica', 12,'bold'), justify='center')
removed_items_label.pack(side='right', fill='y', padx=10, pady=0)



# Create label for the bill




print_kot_button = tk.Button(root, text="Print KOT", command=lambda:print_kot(current_table),font=("times new roman",15),bg="green",fg="white")
print_kot_button.pack(side='top', padx=10, pady=5, fill='x')

cancel_reason_var = tk.StringVar()
cancel_reason_entry = tk.Entry(root, textvariable=cancel_reason_var,font=("times new roman",15))
cancel_reason_entry.pack(side='top', padx=10, pady=25, fill='x')

cancel_kot_button = tk.Button(root, text="Cancel KOT", command=cancel_kot,font=("times new roman",15),bg="green",fg="white")
cancel_kot_button.pack(side='top', padx=10, pady=5, fill='x')



# Create an Entry widget for entering the reason for cancellation





mode_var = tk.StringVar()
mode_options = ["DINE IN", "TAKE AWAY"]
mode_dropdown =ttk.Combobox(root, textvariable=mode_var, values=mode_options,font=("times new roman",15))
mode_dropdown.pack(side='top', padx=10, pady=5, fill='x')
mode_dropdown.set("DINE IN")


#steward_name = steward_dropdown.get()
 # Get the selected steward from the dropdown


print_bill = tk.Button(root, text="Print Bill", command=print_bill,font=("times new roman",15),bg="green",fg="white")
print_bill.pack(side='top', padx=10, pady=5, fill='x')

payment_var = tk.StringVar()
payment_options = ["Cash", "Card", "UPI","NC",""]
payment_dropdown =ttk.Combobox(root, textvariable=payment_var, values=payment_options,font=("times new roman",15))
payment_dropdown.pack(side='top', padx=10, pady=5, fill='x')
payment_dropdown.set("")

bill_button = tk.Button(root, text="Close Bill", command=lambda:printfinal(current_table), font=("times new roman", 15), bg="green", fg="white")
bill_button.pack(side='top', padx=10, pady=5, fill='x')

bottomLabel=tk.Label(menu_frame,text="Application created by PixelBridge Technologies. \n For any queries contact:8972422059",font=("calibri",13),background="#003535",foreground="white")
bottomLabel.pack(side="bottom",fill='x')










####-------trial--------##





conn = sqlite3.connect('food_database.db')
cursor = conn.cursor()

# Create a table to store categories
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
''')

   

# Commit the changes and close the connection
conn.commit()
conn.close()



print("Database created and categories table configured.")


#_____----------creating food column in the database=-----------##
# Create or connect to the database
conn = sqlite3.connect('food_database.db')
cursor = conn.cursor()


# Insert categories into the table
cursor.execute('SELECT COUNT(*) FROM categories')
existing_categories_count = cursor.fetchone()[0]

if existing_categories_count == 0:
    # Insert categories into the table
    categories = ["SOUPS & DIMSUM", "SALADS & CONTINENTAL", "THAI WOK", "MEXICAN", "EUROPEAN", "GREEK", "ITALIAN(PASTA & PIZZA)","HAMRO KALIMPONG",
                  "INDIAN SECTION","DESSERTS","ALL DAY BREAKFAST","TEA & COFFEE","SHAKES AND PARFAITS","MOCKTAILS","OPEN FOOD","OPEN BEVERAGE"]
    cursor.executemany('INSERT INTO categories (name) VALUES (?)', [(category,) for category in categories])
    conn.commit()
    print("Categories inserted.")

# Create a table to store food items
cursor.execute('''
    CREATE TABLE IF NOT EXISTS food (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        FOREIGN KEY (category) REFERENCES categories (name)
    )
''')

conn.commit()
conn.close()

print("Database created and categories inserted.")

def create_category_buttons():
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM categories')
    categories = [row[0] for row in cursor.fetchall()]
    
    for category in categories:
        category_button = tk.Button(menu_frame, text=category, font=("times new roman",12),command=lambda cat=category: display_category_food(cat))
        category_button.pack(side='top', fill='x', padx=10, pady=1)


    
    conn.close()

create_category_buttons()
populate_food_listbox()

customer=tk.Button(take_away_buttons_frame,bg="green", fg="white",text='Customer Registration',font=("times new roman",15),command=register)
customer.pack(side='right',fill='x')


conn = sqlite3.connect('food_database.db')
cursor = conn.cursor()

# Create the 'bills' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill (
        id INTEGER PRIMARY KEY,
        item TEXT,
        total_amount REAL NOT NULL,
        date DATE NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Bills table created.")



def insert_new_bill(item,total_amount, date):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    # Insert the new bill into the 'bills' table
    cursor.execute('INSERT INTO bill(item,total_amount, date) VALUES (?,?, ?)', (item,total_amount, date))

    conn.commit()
    conn.close()

    print("New bill inserted into the database.")



def display_total_sales():
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    # Calculate the total sales for the day
    cursor.execute('SELECT SUM(total_amount) FROM bills WHERE date = ?', (current_date,))
    total_sales = cursor.fetchone()[0]

    conn.close()

    # Create a top-level window to display the total sales
    total_sales_window = tk.Toplevel(root)
    total_sales_window.title("Total Sales")

    # Create a label to display the total sales
    total_sales_label = tk.Label(total_sales_window, text=f"Total Sales for {current_date}: Rs{total_sales:.2f}", font=("times new roman", 12, "bold"))
    total_sales_label.pack(padx=20, pady=20)

# Create a button to display the total sales
total_sales_button = tk.Button(root, text="Display Total Sales", command=display_total_sales)
total_sales_button.pack(padx=10, pady=10)





# Connect to the database
conn = sqlite3.connect('food_database.db')
cursor = conn.cursor()

# Create the 'bills' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY,
        total_amount REAL NOT NULL,
        date DATE NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Bills table created.")







def insert_new_dish():
    new_dish_name = dish_name_var.get()  # Use dish_name_var.get() to retrieve the value
    new_dish_price = float(dish_price_var.get())  # Use dish_price_var.get() to retrieve the value
    selected_category = category_var.get()

    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO food (name, price) VALUES (?, ?)', (new_dish_name, new_dish_price))
    conn.commit()

    cursor.execute('UPDATE food SET category = ? WHERE name = ?', (selected_category, new_dish_name))
    

    populate_food_listbox(selected_category)

    conn.commit()

    conn.close()

    messagebox.showinfo("information","dish successfully added!")
    top_level.destroy()

def authenticate_addition():
    # Create a password dialog
    password = simpledialog.askstring("Authentication", "Enter password to add a new dish:", show='*')
    
    # Check if the entered password is correct
    if password == "Themeltingpot009":  # Replace with the actual password
        open_add_dish_window()  # Call the remove_dish function if password is correct
    else:
        messagebox.showerror("Authentication Failed", "Incorrect password.")




# Create a button to open the top-level window
def open_add_dish_window():
    global top_level
    top_level = tk.Toplevel(root,bg="#003535")
    global dish_name_var
    global dish_price_var
    global category_var

    # Create entry fields and labels
    tk.Label(top_level, text="Dish Name:",background="#003535",fg="white",font=("times new roman",15)).grid(row=0, column=0, padx=10, pady=5)
    dish_name_var = tk.StringVar()  # Create a StringVar to store the entry value
    dish_name_entry = tk.Entry(top_level, textvariable=dish_name_var,font=("times new roman",15))  # Use textvariable to bind the StringVar
    dish_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(top_level, text="Dish Price:",background="#003535",fg="white",font=("times new roman",15)).grid(row=1, column=0, padx=10, pady=5)
    dish_price_var = tk.StringVar()  # Create a StringVar to store the entry value
    dish_price_entry = tk.Entry(top_level, textvariable=dish_price_var,font=("times new roman",15))  # Use textvariable to bind the StringVar
    dish_price_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(top_level, text="Category:",background="#003535",fg="white",font=("times new roman",15)).grid(row=2, column=0, padx=10, pady=5)
    categories = ["SOUPS & DIMSUM", "SALADS & CONTINENTAL", "THAI WOK", "MEXICAN", "EUROPEAN", "GREEK", "ITALIAN(PASTA & PIZZA)","HAMRO KALIMPONG",
                  "INDIAN SECTION","DESSERTS","ALL DAY BREAKFAST","TEA & COFFEE","SHAKES AND PARFAITS","MOCKTAILS","OPEN FOOD","OPEN BEVERAGE"]
    category_var = tk.StringVar(value=categories[0])
    category_dropdown = ttk.Combobox(top_level, textvariable=category_var, values=categories,font=("times new roman",15))
    category_dropdown.grid(row=2, column=1, padx=10, pady=5)

    add_button = tk.Button(top_level, text="Add Dish", command=insert_new_dish,font=("times new roman",15),background="green",fg="white")
    add_button.grid(row=3, columnspan=2, padx=10, pady=10)

# Create a button to open the top-level window
add_dish_button = tk.Button(menu_frame, text="Add New Dish",font=("times new roman",15),bg="green",fg="white", command=authenticate_addition)
add_dish_button.pack(padx=10, pady=0,side="top",fill="x")

def authenticate_removal():
    # Create a password dialog
    password = simpledialog.askstring("Authentication", "Enter password to remove dish:", show='*')
    
    # Check if the entered password is correct
    if password == "Themeltingpot009":  # Replace with the actual password
        remove_dish()  # Call the remove_dish function if password is correct
    else:
        messagebox.showerror("Authentication Failed", "Incorrect password. Dish removal cancelled.")


def remove_dish():
    selected_item = food_listbox.get(food_listbox.curselection())
    
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM food WHERE name = ?', (selected_item,))
    conn.commit()
    
    conn.close()

    # Refresh the food listbox
    update_listbox(None)  # Call the update_listbox function to refresh the listbox

# Create a button to remove a dish
remove_dish_button = tk.Button(menu_frame, text="Remove Dish", command=authenticate_removal,font=("times new roman",15),background="red",foreground="white")
remove_dish_button.pack(padx=10, pady=0,fill="x")

def calculate_sales():
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    # Calculate sales for individual categories
    cursor.execute('SELECT category, SUM(price) FROM food GROUP BY category')
    category_sales = cursor.fetchall()

    # Calculate total sales for food
    cursor.execute('SELECT SUM(price) FROM food')
    total_food_sales = cursor.fetchone()[0]

    # Calculate total sales for beverages
    cursor.execute('SELECT SUM(price) FROM food WHERE category = "Beverages"')
    total_beverages_sales = cursor.fetchone()[0]

    conn.close()

    return category_sales, total_food_sales, total_beverages_sales

def display_sales():
    category_sales, total_food_sales, total_beverages_sales = calculate_sales()

    sales_text = "Sales Report\n\n"
    sales_text += "Sales by Category:\n"
    for category, sales in category_sales:
        sales_text += f"{category}: Rs{sales:.2f}\n"

    sales_text += "\nTotal Food Sales: Rs{:.2f}\n".format(total_food_sales)
    sales_text += "Total Beverages Sales: Rs{:.2f}\n".format(total_beverages_sales)

    # Calculate total sales for the day excluding NC
    nc_sales = 0  # Assuming NC sales are 0
    total_sales = total_food_sales + total_beverages_sales - nc_sales
    sales_text += "\nTotal Sales for the Day (excluding NC): Rs{:.2f}".format(total_sales)

    sales_window = tk.Toplevel(root)
    sales_label = tk.Label(sales_window, text=sales_text, font=("times new roman", 12))
    sales_label.pack(padx=10, pady=10)

# Create a button to display closing sales
closing_sales_button = tk.Button(root, text="Closing Sales", command=display_sales)
closing_sales_button.pack(padx=10, pady=10)










# Start the tkinter main loop
root.mainloop()
