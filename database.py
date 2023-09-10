import sqlite3

def create_table():
    conn = sqlite3.connect('account_data.db')
    cursor = conn.cursor()

    # Create a table for account IDs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        parent_account_id TEXT NOT NULL,
        child_account_id TEXT NOT NULL,
        parent_balance REAL NOT NULL,
        child_balance REAL NOT NULL
    )
    ''')
                
    # Commit changes and close connection
    conn.commit()
    conn.close()

#insert data
def insert_account(parent_account_id, child_account_id, parent_balance, child_balance):
    conn = sqlite3.connect('account_data.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO accounts (parent_account_id, child_account_id, parent_balance, child_balance) VALUES (?, ?, ?, ?)', 
                   (parent_account_id, child_account_id, parent_balance, child_balance))

    conn.commit()
    conn.close()

#retrieve data (format: list of tuples)
def get_accounts():
    conn = sqlite3.connect('account_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()

    conn.close()
    return accounts

def is_parent_id(id):
    for tuple in get_accounts():
        if tuple[1] == id:
            return True
    return False

def is_child_id(id):
    for tuple in get_accounts():
        if tuple[2] == id:
            return True
    return False

def get_account_info(id):
    for tuple in get_accounts():
        if tuple[1] == id or tuple[2] == id:
            return (tuple[1], tuple[2], tuple[3], tuple[4])
    return None

def update_parent(parent_id, newBalance):
    conn = sqlite3.connect('account_data.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE accounts SET parent_balance = ? WHERE parent_account_id = ?', (newBalance, parent_id))

    conn.commit()
    conn.close()

def update_child(child_id, newBalance):
    conn = sqlite3.connect('account_data.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE accounts SET child_balance = ? WHERE child_account_id = ?', (newBalance, child_id))

    conn.commit()
    conn.close()



