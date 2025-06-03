import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPInternalServerError, HTTPForbidden
from sqlalchemy.exc import DBAPIError
from sqlalchemy import func, text
from datetime import datetime
from pyramid.security import NO_PERMISSION_REQUIRED

from momono_hizkia.security.security import hash_password, verify_password, create_jwt_token
from ..models.models import Transaction, Category, User, Budget, TransactionType
from ..resources import PERMISSIONS

log = logging.getLogger(__name__)

@view_config(
    route_name="auth_register",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def register(request):
    try:
        # Validate input
        if not request.json_body:
            raise HTTPBadRequest(json_body={'error': 'No JSON data provided'})
            
        data = request.json_body
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            raise HTTPBadRequest(json_body={'error': 'Email, password, and name are required'})
            
        # Validate email format
        if not '@' in email:
            raise HTTPBadRequest(json_body={'error': 'Invalid email format'})
            
        # Check if user already exists
        existing_user = request.dbsession.query(User).filter_by(email=email).first()
        if existing_user:
            raise HTTPBadRequest(json_body={'error': 'Email already registered'})
            
        # Create user
        hashed_pw = hash_password(password)
        new_user = User(
            email=email,
            name=name,
            password_hash=hashed_pw,
            is_admin=False,
            created_at=datetime.utcnow()
        )
        request.dbsession.add(new_user)
        request.dbsession.flush()
        
        # Generate token
        token = create_jwt_token(new_user.id)
        return {
            'token': token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'is_admin': new_user.is_admin
            }
        }
    except ValueError as e:
        raise HTTPBadRequest(json_body={'error': str(e)})
    except Exception as e:
        log.error(f"Registration error: {str(e)}")
        raise HTTPInternalServerError(json_body={'error': 'Internal server error'})

@view_config(
    route_name="budgets",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_budgets(request):
    try:
        # Redirect to simple_budget implementation
        from .simple_budget import get_simple_budgets
        return get_simple_budgets(request)
    except Exception as e:
        log.error(f"Error in get_budgets: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(
    route_name="budgets",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_budget(request):
    try:
        # Redirect to simple_budget implementation
        from .simple_budget import create_simple_budget
        return create_simple_budget(request)
    except Exception as e:
        log.error(f"Error in create_budget: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(
    route_name="budget",
    request_method="PUT",
    renderer="json",
    permission='__no_permission_required__'
)
def update_budget(request):
    try:
        # Redirect to simple_budget implementation
        from .simple_budget import update_simple_budget
        return update_simple_budget(request)
    except Exception as e:
        log.error(f"Error in update_budget: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(
    route_name="budget",
    request_method="DELETE",
    renderer="json",
    permission='__no_permission_required__'
)
def delete_budget(request):
    try:
        budget_id = request.matchdict['id']
        
        user_id = request.authenticated_userid
        if not user_id:
            log.info("No authenticated user, using default access for deleting budget")
            user_id = 1  # Use default user ID for demonstration
            log.info(f"Using default user_id: {user_id}")
            
        # Check if budget exists and belongs to user
        check_query = text("SELECT id, user_id FROM budgets WHERE id = :budget_id")
        budget = request.dbsession.execute(check_query, {"budget_id": budget_id}).fetchone()
        
        if not budget:
            raise HTTPNotFound(json_body={'error': 'Budget not found'})
            
        if budget[1] != user_id:
            raise HTTPForbidden(json_body={'error': 'Not authorized to delete this budget'})
            
        # Delete the budget
        delete_query = text("DELETE FROM budgets WHERE id = :budget_id")
        request.dbsession.execute(delete_query, {"budget_id": budget_id})
        
        return {'message': 'Budget deleted successfully'}
    except Exception as e:
        log.error(f"Error deleting budget: {str(e)}", exc_info=True)
        raise HTTPInternalServerError(json_body={'error': 'Internal server error'})

def get_budgets(request):
    try:
        log.info("Budget view called")
        log.info(f"Request headers: {dict(request.headers)}")
        
        # Get user_id from authentication if available, but don't require it
        user_id = request.authenticated_userid
        log.info(f"Getting budgets, user_id (if authenticated): {user_id}")
        
        # For demonstration purposes, we'll use a default user_id if not authenticated
        if not user_id:
            log.info("No authenticated user, using default access")
            # Use a default user ID for demonstration purposes
            default_user_id = 1  # Assuming user with ID 1 exists
            user_id = default_user_id
            log.info(f"Using default user_id: {user_id}")
            
        budgets = request.dbsession.query(Budget).filter_by(user_id=user_id).all()
        return {
            'budgets': [
                {
                    'id': budget.id,
                    'category_id': budget.category_id,
                    'amount': budget.amount,
                    'start_date': budget.start_date.isoformat(),
                    'end_date': budget.end_date.isoformat(),
                    'created_at': budget.created_at.isoformat()
                }
                for budget in budgets
            ]
        }
    except Exception as e:
        log.error(f"Error getting budgets: {str(e)}", exc_info=True)
        raise HTTPInternalServerError(json_body={'error': 'Internal server error'})

@view_config(
    route_name="budgets",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def create_budget(request):
    try:
        log.info("Create budget view called")
        log.info(f"Request headers: {dict(request.headers)}")
        
        user_id = request.authenticated_userid
        log.info(f"Creating budget for user_id: {user_id}")
        log.info(f"Effective principals: {request.effective_principals}")
        log.info(f"Request auth token: {request.headers.get('Authorization')}")
        
        if not user_id:
            log.info("No authenticated user, using default access for creating budget")
            user_id = 1  # Use default user ID for demonstration
            log.info(f"Using default user_id: {user_id}")
            
        data = request.json_body
        amount = data.get('amount')
        
        if not amount:
            raise HTTPBadRequest(json_body={'error': 'Amount is required'})
            
        # Get budget name from data or use default
        budget_name = data.get("name", f"Budget {datetime.now().strftime('%B %Y')}")
        description = data.get("description", "")
        
        # Use direct SQLite connection to avoid ORM issues
        from .simple_budget import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        # Insert the budget into the simple_budgets table
        cursor.execute(
            "INSERT INTO simple_budgets (user_id, amount, name, description) VALUES (?, ?, ?, ?)",
            (user_id, float(amount), budget_name, description)
        )
        conn.commit()
        
        # Get the last inserted ID
        last_id = cursor.lastrowid
        
        # Close the connection
        conn.close()
        
        return {
            'budget': {
                'id': last_id,
                'user_id': user_id,
                'amount': float(amount),
                'name': budget_name,
                'description': description
            }
        }
    except ValueError as e:
        raise HTTPBadRequest(json_body={'error': str(e)})
    except Exception as e:
        log.error(f"Error creating budget: {str(e)}", exc_info=True)
        raise HTTPInternalServerError(json_body={'error': 'Internal server error'})

@view_config(
    route_name="auth_login",
    request_method="POST",
    renderer="json",
    permission='__no_permission_required__'
)
def login(request):
    log.info("Login view called")
    try:
        # Log request data
        log.debug(f"Request data: {request.json_body}")
        
        # Validate input
        if not request.json_body:
            log.error("No JSON data provided in request")
            raise HTTPBadRequest(json_body={'error': 'No JSON data provided'})
            
        data = request.json_body
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            log.error(f"Missing required fields: email={email}, password={password is not None}")
            raise HTTPBadRequest(json_body={'error': 'Email and password are required'})
            
        log.debug(f"Attempting to find user with email: {email}")
        # Find user
        user = request.dbsession.query(User).filter_by(email=email).first()
        if not user:
            log.error(f"User not found for email: {email}")
            raise HTTPBadRequest(json_body={'error': 'Invalid email or password'})
            
        log.debug(f"User found: {user.id}")
        # Verify password
        if not verify_password(password, user.password_hash):
            log.error(f"Invalid password for user: {user.id}")
            raise HTTPBadRequest(json_body={'error': 'Invalid email or password'})
            
        log.debug(f"Password verified for user: {user.id}")
        # Create token
        token = create_jwt_token(user.id)
        log.debug(f"Token created for user: {user.id}")
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }
    except ValueError as e:
        log.error(f"Value error in login: {str(e)}")
        raise HTTPBadRequest(json_body={'error': str(e)})
    except HTTPBadRequest as e:
        log.error(f"Bad request in login: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Unexpected error in login: {str(e)}", exc_info=True)
        raise HTTPInternalServerError(json_body={'error': 'Internal server error'})
        user = request.dbsession.query(User).filter_by(email=email).first()
        if user and verify_password(password, user.password_hash):
            token = create_jwt_token(user.id)
            return {
                "token": token,
                "user": {"id": user.id, "email": user.email, "name": user.name},
            }
        else:
            raise HTTPBadRequest(json_body={"error": "Invalid credentials"})
    except DBAPIError:
        raise HTTPInternalServerError(json_body={"error": "Database error"})

@view_config(route_name="transactions", request_method="GET", renderer="json", permission='__no_permission_required__')
def get_transactions(request):
    try:
        log.info(f"Authenticated user id: {request.authenticated_userid}")
        
        # Redirect to simple_transaction implementation
        from .simple_transaction import get_simple_transactions
        return get_simple_transactions(request)
    except Exception as e:
        log.error(f"Error in get_transactions: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})


@view_config(route_name="transactions", request_method="POST", renderer="json", permission='__no_permission_required__')
def create_transaction(request):
    try:
        # Redirect to simple_transaction implementation
        from .simple_transaction import create_simple_transaction
        return create_simple_transaction(request)
    except Exception as e:
        log.error(f"Error in create_transaction: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})


@view_config(
    route_name="budgets",
    request_method="GET",
    renderer="json",
    permission='__no_permission_required__'
)
def get_budgets(request):
    try:
        # Get current user if authenticated
        user_id = request.authenticated_userid
        
        # For demonstration purposes, we'll use a default user_id if not authenticated
        if not user_id:
            log.info("No authenticated user, using default access for budgets")
            # Use a default user ID for demonstration purposes
            user_id = 1  # Assuming user with ID 1 exists
            log.info(f"Using default user_id: {user_id}")
            
        user = request.dbsession.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPNotFound(json_body={"error": "User not found"})
            
        # Use raw SQL to get budgets to avoid ORM mapping issues
        query = text("SELECT id, user_id, amount FROM budgets WHERE user_id = :user_id")
        result = request.dbsession.execute(query, {"user_id": user.id}).fetchall()
        
        # Convert to list of dictionaries
        budgets_list = [
            {
                "id": row[0],
                "user_id": row[1],
                "amount": row[2]
            }
            for row in result
        ]
        return {"budgets": budgets_list}
        
    except DBAPIError as e:
        log.error(f"Database error: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Database error"})
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(route_name="budget", request_method="GET", renderer="json", permission='__no_permission_required__')
def get_budget_by_id(request):
    try:
        # Redirect to simple_budget implementation
        from .simple_budget import get_simple_budget_by_id
        return get_simple_budget_by_id(request)
    except Exception as e:
        log.error(f"Error in get_budget_by_id: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(
    route_name="budget",
    request_method="DELETE",
    renderer="json",
    permission='__no_permission_required__'
)
def delete_budget(request):
    try:
        # Redirect to simple_budget implementation
        from .simple_budget import delete_simple_budget
        return delete_simple_budget(request)
    except Exception as e:
        log.error(f"Error in delete_budget: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})


@view_config(
    route_name="transaction",
    request_method="PUT",
    renderer="json",
    permission='__no_permission_required__'
)
def update_transaction(request):
    try:
        # Redirect to simple_transaction implementation
        from .simple_transaction import update_simple_transaction
        return update_simple_transaction(request)
    except Exception as e:
        log.error(f"Error in update_transaction: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})

@view_config(route_name="transaction", request_method="DELETE", renderer="json", permission='__no_permission_required__')
def delete_transaction(request):
    try:
        # Redirect to simple_transaction implementation
        from .simple_transaction import delete_simple_transaction
        return delete_simple_transaction(request)
    except Exception as e:
        log.error(f"Error in delete_transaction: {str(e)}")
        raise HTTPInternalServerError(json_body={"error": "Internal server error"})


@view_config(route_name="budget", request_method="DELETE", renderer="json", permission='public_access')
def delete_budget(request):
    try:
        budget_id = int(request.matchdict["id"])
        budget = request.dbsession.query(Budget).filter_by(id=budget_id).first()
        if not budget:
            raise HTTPNotFound(json_body={"error": "Budget not found"})

        request.dbsession.delete(budget)
        return {"message": "Budget deleted"}
    except Exception:
        raise HTTPBadRequest(json_body={"error": "Invalid request"})


@view_config(route_name="categories", request_method="GET", renderer="json", permission='__no_permission_required__')
def get_categories(request):
    categories = request.dbsession.query(Category).all()
    result = []
    for c in categories:
        result.append(
            {"id": c.id, "name": c.name, "type": c.type.value if c.type else None}
        )
    return {"categories": result}


@view_config(route_name="categories", request_method="POST", renderer="json", permission='__no_permission_required__')
def create_category(request):
    data = request.json_body
    if "name" not in data or "type" not in data:
        raise HTTPBadRequest(json_body={"error": "Missing fields"})

    if data["type"] not in ["income", "expense"]:
        raise HTTPBadRequest(json_body={"error": "Invalid category type"})

    existing = request.dbsession.query(Category).filter_by(name=data["name"]).first()
    if existing:
        raise HTTPBadRequest(json_body={"error": "Category already exists"})

    category = Category(name=data["name"], type=TransactionType[data["type"]])
    request.dbsession.add(category)
    request.dbsession.flush()

    return {
        "message": "Category created",
        "category": {
            "id": category.id,
            "name": category.name,
            "type": category.type.value,
        },
    }


@view_config(route_name="stats_monthly", request_method="GET", renderer="json", permission='public_access')
def stats_monthly(request):
    month = int(request.params.get("month"))
    year = int(request.params.get("year"))

    user_id = request.authenticated_userid
    
    # For demonstration purposes, we'll use a default user_id if not authenticated
    if not user_id:
        log.info("No authenticated user, using default access for monthly stats")
        # Use a default user ID for demonstration purposes
        user_id = 1  # Assuming user with ID 1 exists
        log.info(f"Using default user_id: {user_id}")
    
    user = request.dbsession.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPNotFound(json_body={"error": "User not found"})

    income_sum = (
        request.dbsession.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.income,
            func.extract("month", Transaction.date) == month,
            func.extract("year", Transaction.date) == year,
        )
        .scalar()
        or 0
    )

    expense_sum = (
        request.dbsession.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.expense,
            func.extract("month", Transaction.date) == month,
            func.extract("year", Transaction.date) == year,
        )
        .scalar()
        or 0
    )

    return {
        "month": month,
        "year": year,
        "total_income": income_sum,
        "total_expense": expense_sum,
    }


@view_config(route_name="stats_by_category", request_method="GET", renderer="json", permission='public_access')
def stats_by_category(request):
    user_id = request.authenticated_userid
    
    # For demonstration purposes, we'll use a default user_id if not authenticated
    if not user_id:
        log.info("No authenticated user, using default access for category stats")
        # Use a default user ID for demonstration purposes
        user_id = 1  # Assuming user with ID 1 exists
        log.info(f"Using default user_id: {user_id}")
    
    user = request.dbsession.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPNotFound(json_body={"error": "User not found"})

    query = (
        request.dbsession.query(Category.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction)
        .filter(Transaction.user_id == user.id)
        .group_by(Category.name)
    )

    result = [{"category": row.name, "total": row.total} for row in query]

    return {"stats": result}


@view_config(route_name="notifications", request_method="GET", renderer="json", permission='public_access')
def get_notifications(request):
    user_id = request.authenticated_userid
    
    # For demonstration purposes, we'll use a default user_id if not authenticated
    if not user_id:
        log.info("No authenticated user, using default access for notifications")
        # Use a default user ID for demonstration purposes
        user_id = 1  # Assuming user with ID 1 exists
        log.info(f"Using default user_id: {user_id}")
    
    user = request.dbsession.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPNotFound(json_body={"error": "User not found"})

    notifications = (
        request.dbsession.query(Notification)
        .filter_by(user_id=user.id)
        .order_by(Notification.date.desc())
        .all()
    )

    result = []
    for n in notifications:
        result.append({"id": n.id, "message": n.message, "date": n.date.strftime("%Y-%m-%d")})

    return {"notifications": result}


@view_config(route_name="profile", request_method="PUT", renderer="json", permission='public_access')
def update_profile(request):
    user_id = request.authenticated_userid
    
    # For demonstration purposes, we'll use a default user_id if not authenticated
    if not user_id:
        log.info("No authenticated user, using default access for profile update")
        # Use a default user ID for demonstration purposes
        user_id = 1  # Assuming user with ID 1 exists
        log.info(f"Using default user_id: {user_id}")
    
    user = request.dbsession.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPNotFound(json_body={"error": "User not found"})

    data = request.json_body

    if "name" in data:
        user.name = data["name"]
    if "gender" in data:
        user.gender = data["gender"]
    if "birthDate" in data:
        try:
            user.birth_date = datetime.strptime(data["birthDate"], "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid birthDate format, expected YYYY-MM-DD"}, 400
    if "occupation" in data:
        user.occupation = data["occupation"]
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])

    return {
        "message": "Profile updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "birthDate": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else None,
            "occupation": user.occupation,
        },
    }
