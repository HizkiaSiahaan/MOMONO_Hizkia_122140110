import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPInternalServerError
from pyramid.response import Response
import json
import sqlite3
import os

log = logging.getLogger(__name__)

# Get the database path
def get_db_path():
    # Get the correct path to the database file
    # The database should be in the root of the project, not in the momono_hizkia subfolder
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'momono_hizkia.sqlite')
    log.info(f"Using database at: {db_path}")
    return db_path

# Simple function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

# Ensure the simple_budgets table exists
def ensure_simple_budgets_table():
    try:
        db_path = get_db_path()
        log.info(f"Ensuring simple_budgets table exists in database at: {db_path}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if simple_budgets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_budgets'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            log.info("simple_budgets table does not exist, creating it now...")
            # Create a simple budgets table if it doesn't exist
            cursor.execute('''
                CREATE TABLE simple_budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT
                )
            ''')
            conn.commit()
            log.info("Created simple_budgets table successfully")
        else:
            log.info("simple_budgets table already exists")
            # Check if the category column exists
            cursor.execute("PRAGMA table_info(simple_budgets)")
            columns = [column[1] for column in cursor.fetchall()]
            log.info(f"Existing columns in simple_budgets: {columns}")
            
            if 'category' not in columns:
                log.info("Adding category column to simple_budgets table")
                # Add category column if it doesn't exist
                cursor.execute("ALTER TABLE simple_budgets ADD COLUMN category TEXT")
                conn.commit()
                log.info("Added category column to simple_budgets table successfully")
        
        # Verify table structure after changes
        cursor.execute("PRAGMA table_info(simple_budgets)")
        columns = cursor.fetchall()
        log.info(f"Final table structure: {columns}")
        
        conn.close()
    except Exception as e:
        log.error(f"Error ensuring simple_budgets table: {str(e)}")
        raise

@view_config(
    route_name="simple_budgets",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_simple_budgets(request):
    try:
        # Make sure the table exists
        ensure_simple_budgets_table()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user_id from request or use default
        user_id = 1  # Default user_id
        log.info(f"Fetching budgets for user_id: {user_id}")
            
        # Get all budgets for the user
        cursor.execute("SELECT id, user_id, amount, name, description, category FROM simple_budgets WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        log.info(f"Found {len(rows)} budgets in database")
        
        budgets = []
        for row in rows:
            budget_dict = dict(row)
            log.info(f"Budget: {budget_dict}")
            budgets.append(budget_dict)
        
        conn.close()
        return {"budgets": budgets}
    except Exception as e:
        log.error(f"Error retrieving budgets: {str(e)}")
        # Return empty list instead of error to prevent frontend issues
        return {"budgets": [], "error": str(e)}

@view_config(
    route_name="simple_budgets",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_simple_budget(request):
    try:
        # Make sure the table exists
        ensure_simple_budgets_table()
        
        data = request.json_body
        amount = data.get('amount')
        description = data.get('description', '')
        category = data.get('category', '')
        # Use category as name if name is not provided but category is
        if data.get('name'):
            name = data.get('name')
        elif category:
            name = f'Budget for {category}'
        else:
            name = f'Budget {amount}'
        
        if not amount:
            return Response(
                json.dumps({"error": "Amount is required"}),
                status=400,
                content_type='application/json'
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new budget
        cursor.execute(
            "INSERT INTO simple_budgets (user_id, amount, name, description, category) VALUES (?, ?, ?, ?, ?)",
            (1, amount, name, description, category)
        )
        conn.commit()
        
        # Get the last inserted ID
        budget_id = cursor.lastrowid
        log.info(f"Created new budget with ID: {budget_id}, category: {category}")
        
        # Get the inserted budget
        cursor.execute("SELECT id, user_id, amount, name, description, category FROM simple_budgets WHERE id = ?", (budget_id,))
        budget = dict(cursor.fetchone())
        
        conn.close()
        return {"budget": budget}
    except Exception as e:
        log.error(f"Error creating budget: {str(e)}")
        return Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        )

@view_config(
    route_name="simple_budget",
    request_method="PUT",
    renderer="json",
    permission='__no_permission_required__'
)
def update_simple_budget(request):
    try:
        # Make sure the table exists
        ensure_simple_budgets_table()
        
        budget_id = request.matchdict['id']
        data = request.json_body
        amount = data.get('amount')
        description = data.get('description')
        category = data.get('category', '')
        
        if not amount:
            return Response(
                json.dumps({"error": "Amount is required"}),
                status=400,
                content_type='application/json'
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if budget exists
        cursor.execute("SELECT id FROM simple_budgets WHERE id = ?", (budget_id,))
        if not cursor.fetchone():
            conn.close()
            return Response(
                json.dumps({"error": "Budget not found"}),
                status=404,
                content_type='application/json'
            )
        
        # Update budget
        name = data.get('name', 'Updated Budget')
        cursor.execute(
            "UPDATE simple_budgets SET amount = ?, description = ?, name = ?, category = ? WHERE id = ?",
            (amount, description, name, category, budget_id)
        )
        conn.commit()
        
        # Get the updated budget
        cursor.execute("SELECT id, user_id, amount, name, description, category FROM simple_budgets WHERE id = ?", (budget_id,))
        budget = dict(cursor.fetchone())
        
        conn.close()
        return {"budget": budget}
    except Exception as e:
        log.error(f"Error updating budget: {str(e)}")
        return Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        )

@view_config(
    route_name="simple_budget",
    request_method="DELETE",
    renderer="json",
    permission='__no_permission_required__'
)
def delete_simple_budget(request):
    try:
        # Make sure the table exists
        ensure_simple_budgets_table()
        
        budget_id = request.matchdict['id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if budget exists
        cursor.execute("SELECT id FROM simple_budgets WHERE id = ?", (budget_id,))
        if not cursor.fetchone():
            conn.close()
            return Response(
                json.dumps({"error": "Budget not found"}),
                status=404,
                content_type='application/json'
            )
        
        # Delete budget
        cursor.execute("DELETE FROM simple_budgets WHERE id = ?", (budget_id,))
        conn.commit()
        
        conn.close()
        return {"message": "Budget deleted successfully"}
    except Exception as e:
        log.error(f"Error deleting budget: {str(e)}")
        return Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        )

@view_config(
    route_name="simple_budget",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_simple_budget_by_id(request):
    try:
        # Make sure the table exists
        ensure_simple_budgets_table()
        
        budget_id = request.matchdict['id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the budget
        cursor.execute("SELECT id, user_id, amount, name, description, category FROM simple_budgets WHERE id = ?", (budget_id,))
        budget = cursor.fetchone()
        
        if not budget:
            conn.close()
            return Response(
                json.dumps({"error": "Budget not found"}),
                status=404,
                content_type='application/json'
            )
        
        budget_dict = dict(budget)
        conn.close()
        return {"budget": budget_dict}
    except Exception as e:
        log.error(f"Error getting budget: {str(e)}")
        return Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        )
