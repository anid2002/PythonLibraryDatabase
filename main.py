import csv
import pandas as pd
import sqlite3
import tkinter as tk
import tkinter.simpledialog as simpledialog

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

#print(books)
#print(borrowers)

# Create a connection to the SQLite database
conn = sqlite3.connect('libDataBase.db')
cursor = conn.cursor()

# Create the 'Book Loans' table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS BookLoans (
        Loan_id INTEGER PRIMARY KEY,
        isbn10 TEXT,
        isbn13 TEXT,
        card_id TEXT,
        date_out TEXT,
        due_date TEXT,
        date_in TEXT,
        FOREIGN KEY(isbn10) REFERENCES books(ISBN10),
        FOREIGN KEY(isbn13) REFERENCES books(ISBN13),
        FOREIGN KEY(card_id) REFERENCES borrowers(ID0000id)
    )
""")

conn.commit()
conn.close()

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

    # Clear the listbox
    results_listbox.delete(0, tk.END)

    # Iterate over each row and insert relevant data into the listbox
    for _, row in results.iterrows():
        display_text = f"ISBN10: {row['ISBN10']} | ISBN13: {row['ISBN13']}| Title: {row['Title']} | Author: {row['Authro']}"
        results_listbox.insert(tk.END, display_text)


def checkout_books():
    # Get the selected books
    #selected_books = results_listbox.curselection()
    card_id = simpledialog.askstring("Input", "Please enter your card_id:", parent=root)
    conn = sqlite3.connect('libDataBase.db')
    cursor = conn.cursor()

    # Prompt for borrower's card_id
    #card_id = input("Please enter your card_id: ")

    # Check if card_id exists in borrowers table
    cursor.execute("SELECT * FROM borrowers WHERE ID0000id = ?", (card_id,))
    borrower = cursor.fetchone()

    if borrower is None:
        print("Invalid card_id.")
        return

    # Print the selected books
    #for book in selected_books:
     #   title = results_listbox.get(book)
      #  print(results_listbox.get(book))

       # cursor.execute(f"UPDATE books SET availability = 'unavailable' WHERE title = '{title}'")

    selected_books = results_listbox.curselection()


    for book in selected_books:
        title = results_listbox.get(book)
        print(results_listbox.get(book))

        cursor.execute("SELECT availability, ISBN10, ISBN13 FROM books WHERE title = ?", (title,))
        book_info = cursor.fetchone()
        availability = book_info[0]
        isbn10 = book_info[1]
        isbn13 = book_info[2]

        cursor.execute("SELECT availability FROM books WHERE title = ?", (title,))
        availability = cursor.fetchone()[0]

        if availability == 'available':
            cursor.execute("UPDATE books SET availability = 'unavailable' WHERE title = ?", (title,))
            print(f"Book '{title}' has been checked out.")

# Add entry to BookLoans table
            cursor.execute("""
                INSERT INTO BookLoans (isbn10, isbn13, card_id, date_out, due_date)
                VALUES (?, ?, ?, date('now'), date('now', '+14 day'))
            """, (isbn10, isbn13, card_id))

        else:
            print(f"Book '{title}' is currently unavailable.")

    conn.commit()
    conn.close()

root = tk.Tk()

root.title("Library Database")
root.geometry("800x500")

search_entry = tk.Entry(root)
search_entry.pack(padx=20,pady=20)

search_button = tk.Button(root, text="Search", command=on_search_click)
search_button.pack(padx=20,pady=20)

results_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
results_listbox.pack(padx=10, pady=10)

checkout_button = tk.Button(root, text="Check Out Books", command=checkout_books)
checkout_button.pack(padx=10, pady=10)

root.mainloop()