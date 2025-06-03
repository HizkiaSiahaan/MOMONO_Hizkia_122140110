import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPInternalServerError
from pyramid.response import Response
import json
import sqlite3
import os
from datetime import datetime

log = logging.getLogger(__name__)

# Get the database path
def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'momono.sqlite')

# Simple function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables_exist():
    """Ensure that the simple_transactions and simple_budgets tables exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if simple_transactions table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_transactions'")
    if not cursor.fetchone():
        # Create a simple transactions table if it doesn't exist
        cursor.execute('''
            CREATE TABLE simple_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                category TEXT,
                type TEXT DEFAULT 'expense',
                budget_id INTEGER
            )
        ''')
        conn.commit()
        log.info("Created simple_transactions table")
    
    # Check if simple_budgets table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_budgets'")
    if not cursor.fetchone():
        # Create a simple budgets table if it doesn't exist
        cursor.execute('''
            CREATE TABLE simple_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        log.info("Created simple_budgets table")
    
    conn.close()

@view_config(
    route_name="simple_transactions",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_simple_transactions(request):
    """Get all transactions for a user using the simple_transactions table."""
    try:
        # Ensure tables exist
        ensure_tables_exist()
        
        # Get user ID (use default if not authenticated)
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for transactions")
            user_id = 1  # Use default user ID
            log.info(f"Using default user_id: {user_id}")
        
        # Get all transactions for the user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, amount, description, created_at, category, type, budget_id 
            FROM simple_transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                "id": row["id"],
                "amount": row["amount"],
                "description": row["description"],
                "date": row["created_at"],  # Use date field for frontend compatibility
                "created_at": row["created_at"],
                "category": row["category"] or "Uncategorized",
                "type": row["type"] or "expense",
                "budget_id": row["budget_id"]
            })
        
        conn.close()
        return {"transactions": transactions}
        
    except Exception as e:
        log.error(f"Error getting transactions: {str(e)}")
        return {"error": str(e)}, 500

@view_config(
    route_name="simple_transactions",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_simple_transaction(request):
    """Create a transaction using the simple_transactions table."""
    try:
        # Ensure tables exist
        ensure_tables_exist()
        
        # Get user ID (use default if not authenticated)
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for creating transaction")
            user_id = 1  # Use default user ID
            log.info(f"Using default user_id: {user_id}")
        
        # Get request data
        data = request.json_body
        if "amount" not in data:
            return {"error": "Amount is required"}, 400
        
        # Parse transaction data
        amount = float(data.get("amount", 0))
        description = data.get("description", "")
        transaction_type = data.get("type", "expense")
        category = data.get("category", "Uncategorized")
        
        # Handle date
        date_str = data.get("date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                created_at = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                created_at = datetime.now().strftime("%Y-%m-%d")
                log.warning(f"Invalid date format, using current date: {created_at}")
        else:
            created_at = datetime.now().strftime("%Y-%m-%d")
        
        # Get or create a budget
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if a budget exists for this user
        cursor.execute("SELECT id FROM simple_budgets WHERE user_id = ? LIMIT 1", (user_id,))
        budget_result = cursor.fetchone()
        
        if budget_result:
            budget_id = budget_result["id"]
        else:
            # Create a default budget
            budget_name = f"Default Budget {datetime.now().strftime('%B %Y')}"
            cursor.execute(
                "INSERT INTO simple_budgets (user_id, amount, name, description) VALUES (?, ?, ?, ?)",
                (user_id, 0, budget_name, "Default budget created automatically")
            )
            conn.commit()
            budget_id = cursor.lastrowid
        
        # Insert the transaction
        cursor.execute("""
            INSERT INTO simple_transactions 
            (user_id, amount, description, created_at, category, type, budget_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, 
            amount, 
            description, 
            created_at, 
            category, 
            transaction_type, 
            budget_id
        ))
        
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "message": "Transaction created successfully",
            "transaction": {
                "id": transaction_id,
                "amount": amount,
                "description": description,
                "date": created_at,
                "created_at": created_at,
                "category": category,
                "type": transaction_type,
                "budget_id": budget_id
            }
        }
        
    except Exception as e:
        log.error(f"Error creating transaction: {str(e)}")
        return {"error": str(e)}, 500

@view_config(
    route_name="simple_transaction",
    request_method="PUT",
    renderer="json",
    permission='__no_permission_required__'
)
def update_simple_transaction(request):
    """Update a transaction using the simple_transactions table."""
    try:
        # Ensure tables exist
        ensure_tables_exist()
        
        # Get transaction ID from URL
        transaction_id = request.matchdict.get('id')
        if not transaction_id:
            return {"error": "Transaction ID is required"}, 400
        
        # Get user ID (use default if not authenticated)
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for updating transaction")
            user_id = 1  # Use default user ID
            log.info(f"Using default user_id: {user_id}")
        
        # Get request data
        data = request.json_body
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists and belongs to user
        cursor.execute(
            "SELECT * FROM simple_transactions WHERE id = ? AND user_id = ?", 
            (transaction_id, user_id)
        )
        transaction = cursor.fetchone()
        
        if not transaction:
            conn.close()
            return {"error": "Transaction not found or access denied"}, 404
        
        # Prepare update fields
        update_fields = []
        params = []
        
        if 'amount' in data:
            update_fields.append("amount = ?")
            params.append(float(data['amount']))
            
        if 'description' in data:
            update_fields.append("description = ?")
            params.append(data['description'])
            
        if 'category' in data:
            update_fields.append("category = ?")
            params.append(data['category'])
            
        if 'type' in data:
            update_fields.append("type = ?")
            params.append(data['type'])
            
        if 'date' in data:
            try:
                date_obj = datetime.strptime(data['date'], "%Y-%m-%d")
                created_at = date_obj.strftime("%Y-%m-%d")
                update_fields.append("created_at = ?")
                params.append(created_at)
            except ValueError:
                log.warning(f"Invalid date format: {data['date']}")
        
        if not update_fields:
            conn.close()
            return {"error": "No fields to update"}, 400
        
        # Add transaction ID and user ID to params
        params.append(transaction_id)
        params.append(user_id)
        
        # Update transaction
        query = f"UPDATE simple_transactions SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
        cursor.execute(query, params)
        conn.commit()
        
        # Get updated transaction
        cursor.execute(
            "SELECT * FROM simple_transactions WHERE id = ?", 
            (transaction_id,)
        )
        updated = cursor.fetchone()
        
        if updated:
            result = {
                "id": updated["id"],
                "amount": updated["amount"],
                "description": updated["description"],
                "date": updated["created_at"],
                "created_at": updated["created_at"],
                "category": updated["category"] or "Uncategorized",
                "type": updated["type"] or "expense",
                "budget_id": updated["budget_id"]
            }
        else:
            result = {"error": "Failed to retrieve updated transaction"}
        
        conn.close()
        return {"success": True, "transaction": result}
        
    except Exception as e:
        log.error(f"Error updating transaction: {str(e)}")
        return {"error": str(e)}, 500

@view_config(
    route_name="simple_transaction",
    request_method="DELETE",
    renderer="json",
    permission='__no_permission_required__'
)
def delete_simple_transaction(request):
    """Delete a transaction using the simple_transactions table."""
    try:
        # Get transaction ID from URL
        transaction_id = request.matchdict.get('id')
        if not transaction_id:
            return {"error": "Transaction ID is required"}, 400
        
        # Get user ID (use default if not authenticated)
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for deleting transaction")
            user_id = 1  # Use default user ID
            log.info(f"Using default user_id: {user_id}")
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists and belongs to user
        cursor.execute(
            "SELECT id FROM simple_transactions WHERE id = ? AND user_id = ?", 
            (transaction_id, user_id)
        )
        transaction = cursor.fetchone()
        
        if not transaction:
            conn.close()
            return {"error": "Transaction not found or access denied"}, 404
        
        # Delete transaction
        cursor.execute(
            "DELETE FROM simple_transactions WHERE id = ? AND user_id = ?", 
            (transaction_id, user_id)
        )
        conn.commit()
        
        conn.close()
        return {"success": True, "message": "Transaction deleted successfully"}
        
    except Exception as e:
        log.error(f"Error deleting transaction: {str(e)}")
        return {"error": str(e)}, 500
