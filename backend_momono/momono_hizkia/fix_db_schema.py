import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_budgets_table():
    """
    Fix the budgets table by making the name column nullable or adding it if it doesn't exist.
    """
    try:
        # Try multiple possible database paths
        possible_paths = [
            "momono.sqlite",
            "momono_hizkia/momono.sqlite",
            "momono_hizkia.sqlite"
        ]
        
        conn = None
        for path in possible_paths:
            logger.info(f"Attempting to connect to database at: {path}")
            try:
                conn = sqlite3.connect(path)
                logger.info(f"Successfully connected to database at: {path}")
                break
            except sqlite3.Error as e:
                logger.warning(f"Could not connect to {path}: {e}")
        
        if conn is None:
            raise Exception("Could not connect to any database file")
        cursor = conn.cursor()
        
        # Check if name column exists in budgets table
        cursor.execute("PRAGMA table_info(budgets)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'name' in column_names:
            logger.info("Name column already exists in budgets table")
            
            # Create a temporary table with the same structure but with name column nullable
            cursor.execute("""
            CREATE TABLE budgets_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                name TEXT,
                category_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            """)
            
            # Copy data from the original table to the temporary table
            cursor.execute("""
            INSERT INTO budgets_temp (id, user_id, amount, name, category_id, start_date, end_date)
            SELECT id, user_id, amount, 
                   CASE WHEN name IS NULL THEN 'Default Budget' ELSE name END, 
                   category_id, start_date, end_date 
            FROM budgets
            """)
            
            # Drop the original table
            cursor.execute("DROP TABLE budgets")
            
            # Rename the temporary table to the original table name
            cursor.execute("ALTER TABLE budgets_temp RENAME TO budgets")
            
            logger.info("Successfully made name column nullable in budgets table")
        else:
            # Add name column to budgets table
            cursor.execute("ALTER TABLE budgets ADD COLUMN name TEXT")
            logger.info("Added name column to budgets table")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        logger.info("Database schema update completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        return False

if __name__ == "__main__":
    fix_budgets_table()
