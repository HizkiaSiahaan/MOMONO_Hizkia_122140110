import logging

def includeme(config):
    """Configure routes for MOMONO application."""
    try:
        # Configure logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Public routes
        config.add_route('home', '/')
        config.add_route('auth_login', '/api/auth/login')
        config.add_route('auth_register', '/api/auth/register')
        
        # Protected routes
        config.add_route('auth_logout', '/api/auth/logout')
        config.add_route('user_profile', '/api/user/profile')
        config.add_route('user_settings', '/api/user/settings')
        
        # Transaction routes
        config.add_route('transactions', '/api/transactions')
        config.add_route('transaction', '/api/transactions/{id}')
        
        # Category routes
        config.add_route('categories', '/api/categories')
        config.add_route('category', '/api/categories/{id}')
        
        # Budget routes
        config.add_route('budgets', '/api/budgets')
        config.add_route('budget', '/api/budgets/{id}')
        config.add_route('named_budget', '/api/named-budgets')
        
        # Simple Budget routes (no authentication required)
        config.add_route('simple_budgets', '/api/simple/budgets')
        config.add_route('simple_budget', '/api/simple/budgets/{id}')
        
        # Simple Transaction routes (no authentication required)
        config.add_route('simple_transactions', '/api/simple/transactions')
        config.add_route('simple_transaction', '/api/simple/transactions/{id}')
        
        # Stats routes
        config.add_route('stats_monthly', '/api/stats/monthly')
        config.add_route('stats_by_category', '/api/stats/by-category')
        
        # Notification routes
        config.add_route('notifications', '/api/notifications')
        
        logger.info('Routes configuration completed successfully')
    except Exception as e:
        logger.error(f'Error in routes configuration: {str(e)}')
        raise
    config.add_route('profile', '/api/profile')
