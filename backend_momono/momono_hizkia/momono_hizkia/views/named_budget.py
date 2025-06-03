import logging
import sqlite3
from datetime import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import text

log = logging.getLogger(__name__)

@view_config(
    route_name="named_budget",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_named_budget(request):
    """Create a budget with a name field to avoid NOT NULL constraint errors."""
    try:
        # Get user ID (use default if not authenticated)
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for creating budget")
            user_id = 1  # Use default user ID for demonstration
            log.info(f"Using default user_id: {user_id}")
        
        # Get request data
        data = request.json_body
        amount = data.get('amount')
        
        if not amount:
            return {"error": "Amount is required"}, 400
        
        # Get or generate a name for the budget
        budget_name = data.get("name", f"Budget {datetime.now().strftime('%B %Y')}")
        
        # Use raw SQL to insert budget with name field
        query = text("""
            INSERT INTO budgets (user_id, amount, name) 
            VALUES (:user_id, :amount, :name)
        """)
        
        # Execute the query
        request.dbsession.execute(query, {
            "user_id": user_id,
            "amount": float(amount),
            "name": budget_name
        })
        request.dbsession.flush()
        
        # Get the last inserted ID
        last_id_query = text("SELECT last_insert_rowid()")
        budget_id = request.dbsession.execute(last_id_query).scalar()
        
        return {
            "success": True,
            "message": "Budget created successfully",
            "budget": {
                "id": budget_id,
                "user_id": user_id,
                "amount": float(amount),
                "name": budget_name
            }
        }
        
    except DBAPIError as e:
        log.error(f"Database error: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Database error", "details": str(e)})
    except Exception as e:
        log.error(f"Error creating budget: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})
