from pyramid.security import Allow, Deny, Everyone, Authenticated
from pyramid.httpexceptions import HTTPForbidden
import logging
from .models import User

# Konfigurasi logging
logger = logging.getLogger('momono.resources')
logger.setLevel(logging.INFO)

# Define permission constants
PERMISSIONS = {
    'PUBLIC': 'NO_PERMISSION_REQUIRED',
    'USER': 'authenticated',
    'ADMIN': 'admin',
    'VIEW_DASHBOARD': 'view_dashboard',
    'MANAGE_BUDGETS': 'manage_budgets',
    'VIEW_TRANSACTIONS': 'view_transactions',
    'CREATE_TRANSACTIONS': 'create_transactions',
    'MANAGE_USERS': 'manage_users',
    'MANAGE_SETTINGS': 'manage_settings'
}

class RootFactory:
    def __init__(self, request):
        self.request = request
        
    def __acl__(self):
        """Return ACL for the root resource."""
        try:
            return [
                (Allow, Everyone, 'NO_PERMISSION_REQUIRED'),
                (Allow, Everyone, 'public_access'),  # Add public_access permission for Everyone
                (Allow, Authenticated, 'authenticated'),
                (Allow, Authenticated, 'user'),
                (Allow, Authenticated, 'view'),
                (Allow, Authenticated, 'create'),
                (Allow, Authenticated, 'edit'),
                (Allow, Authenticated, 'delete'),
                (Allow, Authenticated, 'view_dashboard'),
                (Allow, Authenticated, 'manage_budgets'),
                (Allow, Authenticated, 'manage_users'),
                (Allow, Authenticated, 'manage_settings'),
                (Deny, Everyone, 'ALL_PERMISSIONS')
            ]
        except Exception as e:
            logger.error(f'Error getting ACL: {str(e)}')
            return [(Allow, Everyone, 'NO_PERMISSION_REQUIRED')]
