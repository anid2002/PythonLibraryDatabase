import csv
import pandas as pd
import sqlite3
import tkinter as tk

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

    conn = sqlite3.connect('libDataBase.db')
    cursor = conn.cursor()

    # Print the selected books
    #for book in selected_books:
     #   title = results_listbox.get(book)
      #  print(results_listbox.get(book))

       # cursor.execute(f"UPDATE books SET availability = 'unavailable' WHERE title = '{title}'")

    for book in selected_books:
        title = results_listbox.get(book)
        print(results_listbox.get(book))

        cursor.execute("SELECT availability FROM books WHERE title = ?", (title,))
        availability = cursor.fetchone()[0]

        if availability == 'available':
            cursor.execute("UPDATE books SET availability = 'unavailable' WHERE title = ?", (title,))
            print(f"Book '{title}' has been checked out.")
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