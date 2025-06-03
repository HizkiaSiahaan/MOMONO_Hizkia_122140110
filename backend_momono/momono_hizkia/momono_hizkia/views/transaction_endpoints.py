import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPInternalServerError
from datetime import datetime

from ..models.models import Transaction, Category, User, TransactionType

log = logging.getLogger(__name__)

@view_config(route_name="transaction", request_method="GET", renderer="json", permission='public_access')
def get_transaction_by_id(request):
    try:
        transaction_id = int(request.matchdict["id"])
        
        user_id = request.authenticated_userid
        
        # For demonstration purposes, we'll use a default user_id if not authenticated
        if not user_id:
            log.info("No authenticated user, using default access for transaction by ID")
            # Use a default user ID for demonstration purposes
            user_id = 1  # Assuming user with ID 1 exists
            log.info(f"Using default user_id: {user_id}")
        
        transaction = request.dbsession.query(Transaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPNotFound(json_body={"error": "Transaction not found"})

        return {
            "id": transaction.id,
            "type": transaction.type.value if transaction.type else None,
            "amount": transaction.amount,
            "category": transaction.category.name if transaction.category else None,
            "date": transaction.date.strftime("%Y-%m-%d"),
            "description": transaction.description,
        }
    except Exception as e:
        log.error(f"Error getting transaction: {str(e)}")
        raise HTTPBadRequest(json_body={"error": "Invalid request"})


# Commented out to avoid conflict with simple_transaction implementation
# @view_config(route_name="transaction", request_method="PUT", renderer="json", permission='public_access')
def update_transaction(request):
    try:
        transaction_id = int(request.matchdict["id"])
        
        user_id = request.authenticated_userid
        
        # For demonstration purposes, we'll use a default user_id if not authenticated
        if not user_id:
            log.info("No authenticated user, using default access for transaction update")
            # Use a default user ID for demonstration purposes
            user_id = 1  # Assuming user with ID 1 exists
            log.info(f"Using default user_id: {user_id}")
        
        transaction = request.dbsession.query(Transaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPNotFound(json_body={"error": "Transaction not found"})

        data = request.json_body
        
        if "type" in data:
            if data["type"] not in ["income", "expense"]:
                raise HTTPBadRequest(json_body={"error": "Invalid transaction type"})
            transaction.type = TransactionType[data["type"]]
            
        if "amount" in data:
            transaction.amount = float(data["amount"])
            
        if "category" in data:
            category = request.dbsession.query(Category).filter_by(name=data["category"]).first()
            if not category:
                category = Category(name=data["category"], type=transaction.type)
                request.dbsession.add(category)
                request.dbsession.flush()
            transaction.category_id = category.id
            
        if "date" in data:
            try:
                transaction.date = datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                raise HTTPBadRequest(json_body={"error": "Invalid date format, expected YYYY-MM-DD"})
                
        if "description" in data:
            transaction.description = data["description"]

        return {
            "message": "Transaction updated",
            "transaction": {
                "id": transaction.id,
                "type": transaction.type.value,
                "amount": transaction.amount,
                "category": transaction.category.name if transaction.category else None,
                "date": transaction.date.strftime("%Y-%m-%d"),
                "description": transaction.description,
            },
        }
    except Exception as e:
        log.error(f"Error updating transaction: {str(e)}")
        raise HTTPBadRequest(json_body={"error": "Invalid request"})


# Commented out to avoid conflict with simple_transaction implementation
# @view_config(route_name="transaction", request_method="DELETE", renderer="json", permission='public_access')
def delete_transaction(request):
    try:
        transaction_id = int(request.matchdict["id"])
        
        user_id = request.authenticated_userid
        
        # For demonstration purposes, we'll use a default user_id if not authenticated
        if not user_id:
            log.info("No authenticated user, using default access for transaction deletion")
            # Use a default user ID for demonstration purposes
            user_id = 1  # Assuming user with ID 1 exists
            log.info(f"Using default user_id: {user_id}")
        
        transaction = request.dbsession.query(Transaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPNotFound(json_body={"error": "Transaction not found"})

        request.dbsession.delete(transaction)
        return {"message": "Transaction deleted"}
    except Exception as e:
        log.error(f"Error deleting transaction: {str(e)}")
        raise HTTPBadRequest(json_body={"error": "Invalid request"})
