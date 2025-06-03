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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'momono.sqlite')

# Simple function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

@view_config(
    route_name="simple_budgets",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_simple_budgets(request):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if budgets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_budgets'")
        if not cursor.fetchone():
            # Create a simple budgets table if it doesn't exist
            cursor.execute('''
                CREATE TABLE simple_budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT
                )
            ''')
            conn.commit()
            
        # Get all budgets for user_id 1 (default user)
        cursor.execute("SELECT id, user_id, amount, name, description FROM simple_budgets WHERE user_id = 1")
        budgets = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {"budgets": budgets}
    except Exception as e:
        log.error(f"Error getting budgets: {str(e)}")
        return Response(
            json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        )

@view_config(
    route_name="simple_budgets",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_simple_budget(request):
    try:
        data = request.json_body
        amount = data.get('amount')
        description = data.get('description', '')
        name = data.get('name', f'Budget {json.dumps(data)[:20]}...')
        
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
            "INSERT INTO simple_budgets (user_id, amount, name, description) VALUES (?, ?, ?, ?)",
            (1, amount, name, description)
        )
        conn.commit()
        
        # Get the last inserted ID
        budget_id = cursor.lastrowid
        
        # Get the inserted budget
        cursor.execute("SELECT id, user_id, amount, name, description FROM simple_budgets WHERE id = ?", (budget_id,))
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
        budget_id = request.matchdict['id']
        data = request.json_body
        amount = data.get('amount')
        description = data.get('description')
        
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
            "UPDATE simple_budgets SET amount = ?, description = ?, name = ? WHERE id = ?",
            (amount, description, name, budget_id)
        )
        conn.commit()
        
        # Get the updated budget
        cursor.execute("SELECT id, user_id, amount, name, description FROM simple_budgets WHERE id = ?", (budget_id,))
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
        budget_id = request.matchdict['id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the budget
        cursor.execute("SELECT id, user_id, amount, name, description FROM simple_budgets WHERE id = ?", (budget_id,))
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
