from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Deny, Everyone, Authenticated
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register
import logging
import os
from dotenv import load_dotenv
from .models.meta import Base, get_engine, get_session_factory
from .security.security import JWTAuthenticationPolicy
from .cors import cors_tween_factory
from .models import User
from .resources import RootFactory

# Konfigurasi logging
logger = logging.getLogger('momono')
logger.setLevel(logging.INFO)

# Constants
JWT_SECRET = os.getenv('JWT_SECRET', 'godblessyou')
SESSION_SECRET = os.getenv('SESSION_SECRET', 'momono_session_secret')

def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    try:
        logger.info('Starting MOMONO backend application')
        
        # Database setup
        engine = get_engine(settings)
        Base.metadata.bind = engine
        
        # Session factory
        session_factory = SignedCookieSessionFactory(
            SESSION_SECRET,
            timeout=3600,
            cookie_name='momono_session'
        )
        
        # Config setup
        config = Configurator(
            settings=settings,
            session_factory=session_factory,
            root_factory=RootFactory
        )
        
        # Set authentication policy
        authn_policy = JWTAuthenticationPolicy(
            secret=settings.get('jwt.secret', 'godblessyou')
        )
        config.set_authentication_policy(authn_policy)
        
        # Set authorization policy
        config.set_authorization_policy(ACLAuthorizationPolicy())
        
        # Security setup
        # Set default permission to allow access without authentication
        config.set_default_permission('NO_PERMISSION_REQUIRED')
        
        # Define permissions
        permissions = [
            'authenticated',
            'user',
            'view_dashboard',
            'manage_budgets',
            'view',
            'create',
            'edit',
            'delete',
            'manage_users',
            'manage_settings',
            'public_access'  # New permission for public access
        ]
        
        # Add permissions
        for perm in permissions:
            config.add_permission(perm)
            logger.info(f"Added permission: {perm}")
        
        # Override effective_principals untuk menentukan permission berdasarkan role
        def get_user_permissions(request):
            """Get user permissions."""
            try:
                # Always include public_access permission for everyone
                base_permissions = ['public_access', 'NO_PERMISSION_REQUIRED']
                
                user_id = request.authenticated_userid
                logger.info(f"User ID: {user_id}")
                
                if not user_id:
                    logger.info("No user ID found")
                    return base_permissions
                    
                user = request.dbsession.query(User).filter_by(id=user_id).first()
                if not user:
                    logger.info(f"User with ID {user_id} not found")
                    return base_permissions
                    
                # Set permission untuk semua user
                permissions = [
                    'authenticated',
                    'user',
                    'view_dashboard',
                    'manage_budgets',
                    'view',
                    'create',
                    'edit',
                    'delete',
                    'manage_users',
                    'manage_settings'
                ]
                
                # Add base permissions to authenticated user permissions
                permissions.extend(base_permissions)
                
                logger.info(f"Permissions for user {user_id}: {permissions}")
                return permissions
            except Exception as e:
                logger.error(f'Error getting user permissions: {str(e)}', exc_info=True)
                return []
        
        # Set effective_principals di JWTAuthenticationPolicy
        authn_policy.effective_principals = get_user_permissions
        
        # CORS setup
        config.add_tween('momono_hizkia.cors.cors_tween_factory')
        
        # Static files and templates
        config.add_static_view('static', 'static', cache_max_age=3600)
        config.include('pyramid_jinja2')
        
        # Routes and models
        config.include('.models')
        config.include('.routes')
        
        # Scan views
        config.scan()
        
        logger.info('Application configuration completed successfully')
        return config.make_wsgi_app()

    except Exception as e:
        logger.error(f"Error in main configuration: {str(e)}")
        raise
