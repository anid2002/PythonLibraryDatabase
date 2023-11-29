import csv
import pandas as pd
import sqlite3
import tkinter as tk
import datetime
from tkinter import simpledialog, messagebox

# Open the first CSV file and read the data
with open('data/books.csv', 'r', encoding ='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)  # or do something with 'row'

# Open the second CSV file and read the data
with open('data/borrowers.csv', 'r', encoding ='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)  # or do something with 'row'


# Read the CSV files into pandas DataFrames
books = pd.read_csv('data/books.csv', delimiter='\t', encoding='utf-8')
borrowers = pd.read_csv('data/borrowers.csv', delimiter=',', encoding='utf-8')

# Now 'books' and 'borrowers' are DataFrames, you can view them with print()
#print(books)
#print(borrowers)

conn = sqlite3.connect('libDataBase.db')

books.to_sql('books', conn, if_exists='replace', index=False)
cursor = conn.cursor()
cursor.execute("ALTER TABLE books ADD COLUMN availability TEXT DEFAULT 'available'")
conn.commit()

borrowers.to_sql('borrowers', conn, if_exists='replace', index=False)

books = pd.read_sql_query("SELECT * FROM books", conn)
borrowers = pd.read_sql_query("SELECT * FROM borrowers", conn)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT,
        card_id TEXT,
        date_out TEXT,
        due_date TEXT,
        date_in TEXT
    )
""")
conn.commit()

#print(books)
#print(borrowers)

def on_search_click():
    # Get the text from the entry field
    search_text = search_entry.get()

    # Create a connection to the SQLite database
    conn = sqlite3.connect('libDataBase.db')

    # Query the database using pandas
    query = f"SELECT * FROM books WHERE title LIKE '%{search_text}%' OR isbn10 LIKE '%{search_text}%' OR isbn13 LIKE '%{search_text}%' OR authro LIKE '%{search_text}%'"
    results = pd.read_sql_query(query, conn)

    # Print the results
    print(results)

    # Close the connection
    conn.close()

    results_listbox.delete(0, tk.END)

    for _, row in results.iterrows():
        results_listbox.insert(tk.END, row['Title'])


def checkout_books():
    # Get the selected books
    selected_books = results_listbox.curselection()

    card_id = card_id = simpledialog.askstring("Input", "Please enter your card ID:", parent=root)

    conn = sqlite3.connect('libDataBase.db')
    cursor = conn.cursor()

    # Check if the card_id is a valid ID number
    cursor.execute("SELECT * FROM borrowers WHERE ID0000id = ?", (card_id,))
    borrower = cursor.fetchone()
    if borrower is None:
        print("Invalid card ID.")
        messagebox.showinfo("Error", "Invalid card id, try again.")
        return

    # Check if the borrower has already checked out 3 books
    cursor.execute("SELECT COUNT(*) FROM book_loans WHERE card_id = ? AND date_in IS NULL", (card_id,))
    num_loans = cursor.fetchone()[0]

    if num_loans > 3:
        #print("You have reached the maximum number of checkouts (3).")
        messagebox.showinfo("Checkout limit reached", "You have reached the maximum number of checkouts (3).")
        return


    for book in selected_books:
        title = results_listbox.get(book)
        print(results_listbox.get(book))

        cursor.execute("SELECT availability FROM books WHERE title = ?", (title,))
        availability = cursor.fetchone()[0]

        if availability == 'available':
            cursor.execute("UPDATE books SET availability = 'unavailable' WHERE title = ?", (title,))
            print(f"Book '{title}' has been checked out.")

            # Add a new row to the 'book_loans' table
            date_out = datetime.datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO book_loans (isbn, card_id, date_out, due_date) VALUES (?, ?, ?, ?)", (title, card_id, date_out, due_date))

            # Display a message box
            messagebox.showinfo("Success", f"Book '{title}' has been successfully checked out to {card_id}.")
        
        else:
            print(f"Book '{title}' is currently unavailable.")

    conn.commit()
    conn.close()

#NEW FUNCTIONS FOR SEARCHING CHECKED OUT BOOKS AND CHECKING IN BOOKS
def on_search_checkouts_click():
    # Get the text from the entry field
    search_text = search_entry.get()

    # Create a connection to the SQLite database
    conn = sqlite3.connect('libDataBase.db')

    # Query the database using pandas
    query = f"SELECT * FROM book_loans WHERE isbn LIKE '%{search_text}%' OR card_id LIKE '%{search_text}%'"
    results = pd.read_sql_query(query, conn)

    # Print the results
    print(results)

    # Close the connection
    conn.close()

    results_listbox.delete(0, tk.END)

    for _, row in results.iterrows():
        results_listbox.insert(tk.END, row['isbn'])

def checkin_books():
    # Get the selected books
    selected_books = results_listbox.curselection()

    conn = sqlite3.connect('libDataBase.db')
    cursor = conn.cursor()

    # Print the selected books
    for book in selected_books:
        isbn = results_listbox.get(book)
        print(results_listbox.get(book))

        # Set the 'date_in' column to the current date for the selected book
        date_in = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE book_loans SET date_in = ? WHERE isbn = ?", (date_in, isbn))

        # Set the 'availability' column to 'available' in the 'books' table
        cursor.execute("UPDATE books SET availability = 'available' WHERE title = ?", (isbn,))

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Books have been successfully checked in.")

root = tk.Tk()

root.title("Library Database")
root.geometry("800x500")

search_entry = tk.Entry(root)
search_entry.pack(padx=20,pady=20)

search_button = tk.Button(root, text="Search", command=on_search_click)
search_button.pack(padx=20,pady=20)

results_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=500)
results_listbox.pack(padx=10, pady=10)

checkout_button = tk.Button(root, text="Check Out Books", command=checkout_books)
checkout_button.pack(padx=10, pady=10)

checkin_button = tk.Button(root, text="Check In Books", command=checkin_books)
checkin_button.pack(padx=10, pady=10)

root.mainloop()
