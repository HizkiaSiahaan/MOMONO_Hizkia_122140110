import sqlite3
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'momono.sqlite')

print(f"Checking database at: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {tables}")

# Check budgets table structure
try:
    cursor.execute("PRAGMA table_info(budgets);")
    columns = cursor.fetchall()
    print(f"Columns in budgets table: {columns}")
except Exception as e:
    print(f"Error getting budgets table info: {e}")

# Close the connection
conn.close()
