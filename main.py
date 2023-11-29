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

## New Borrower Management (part 4)
import random
add_borrower_window = None # define global variable for add new borrower window 

# generates a random unique ID in the format "ID000100" for new borrowers  
def generate_id():
    conn = sqlite3.connect('libDataBase.db')
    cursor = conn.cursor()
    
    while True:
        # Generate a random 3-digit number
        unique_number = str(random.randint(0, 999)).zfill(3)
        
        # Create the ID by combining "ID000" and the unique number
        id = f"ID000{unique_number}"
        
        # Check if the ID already exists in the BORROWERS table
        cursor.execute("SELECT * FROM borrowers WHERE ID0000id = ?", (id,))
        existing_borrower = cursor.fetchone()
        
        if not existing_borrower:
            # If the ID is unique, return it
            conn.close()
            return id

# Create New Borrower Function 
def create_borrower():
    # creates new GUI window for adding a borrower
    add_borrower_window = tk.Tk()
    add_borrower_window.title("Add New Borrower")

    # GUI elements for borrower infomration 
    borrower_first_name_label = tk.Label(add_borrower_window, text="First Name:")
    borrower_first_name_label.pack()
    borrower_first_name_entry = tk.Entry(add_borrower_window)
    borrower_first_name_entry.pack()

    borrower_last_name_label = tk.Label(add_borrower_window, text="Last Name:")
    borrower_last_name_label.pack()
    borrower_last_name_entry = tk.Entry(add_borrower_window)
    borrower_last_name_entry.pack()

    borrower_ssn_label = tk.Label(add_borrower_window, text="SSN:")
    borrower_ssn_label.pack()
    borrower_ssn_entry = tk.Entry(add_borrower_window)
    borrower_ssn_entry.pack()

    borrower_address_label = tk.Label(add_borrower_window, text="Address:")
    borrower_address_label.pack()
    borrower_address_entry = tk.Entry(add_borrower_window)
    borrower_address_entry.pack()

    def save_borrower():
        # get borrower information from the field above 
        first_name = borrower_first_name_entry.get()
        last_name = borrower_last_name_entry.get()
        ssn = borrower_ssn_entry.get()
        address = borrower_address_entry.get()

        # validate that required fields are all filled; if not filled ouptut message
        if not first_name or not last_name or not ssn or not address:
            # Display an error message to the user
            error_label.config(text="Please fill in all required fields.")
            return

        # generate a unique ID
        id = generate_id()
        
        # insert the new borrower record into database
        conn = sqlite3.connect('libDataBase.db')
        cursor = conn.cursor()

        try:
            # insert into the SQLite database and into the correct columns 
            cursor.execute("INSERT INTO borrowers (ID0000id, first_name, last_name, ssn, address, email, city, state, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (id, first_name, last_name, ssn, address, '', '', '', ''))
            conn.commit()
            conn.close()
            
            # save the borrower information to the borrowers.csv file
            with open('data/borrowers.csv', 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                
                # placeholder values for the empty columsn; information we do not ask for 
                email = ""
                city = ""
                state = ""
                phone = ""
                
                # write the borrower information (including placeholders)
                csv_writer.writerow([id, ssn, first_name, last_name, email, address, city, state, phone])
            
            error_label.config(text="Borrower created successfully.")
        except sqlite3.Error as e:
            print("Error creating borrower:", e)
            error_label.config(text="Error creating borrower.")

        # clear input fields 
        borrower_first_name_entry.delete(0, tk.END)
        borrower_last_name_entry.delete(0, tk.END)
        borrower_ssn_entry.delete(0, tk.END)
        borrower_address_entry.delete(0, tk.END)

    save_button = tk.Button(add_borrower_window, text="Save Borrower", command=save_borrower)
    save_button.pack()

    error_label = tk.Label(add_borrower_window, text="", fg="red")
    error_label.pack()

    add_borrower_window.mainloop()

# add button to open new borrower window 
add_borrower_button = tk.Button(root, text="Add Borrower", command=create_borrower)
add_borrower_button.pack(padx=10, pady=10)

root.mainloop()