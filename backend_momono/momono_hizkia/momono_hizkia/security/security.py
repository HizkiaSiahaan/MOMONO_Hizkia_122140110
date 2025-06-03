import bcrypt
import jwt
import datetime
import logging
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden
from pyramid.security import Allow, Deny, Everyone, Authenticated

# Konfigurasi logging
logger = logging.getLogger('momono.security')
logger.setLevel(logging.INFO)

# Constants
SECRET_KEY = 'godblessyou'  # Ganti dengan secret yang aman
TOKEN_EXPIRY_HOURS = 1

# Permission constants
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

def hash_password(plain_password: str) -> str:
    """Hash password menggunakan bcrypt."""
    try:
        logger.info('Hashing password')
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        logger.info('Password hashed successfully')
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f'Error hashing password: {str(e)}')
        raise HTTPForbidden('Password hashing failed')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password dengan hash yang ada."""
    try:
        logger.info('Verifying password')
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        logger.info(f'Password verification result: {result}')
        return result
    except Exception as e:
        logger.error(f'Error verifying password: {str(e)}')
        raise HTTPForbidden('Password verification failed')

def create_jwt_token(user_id: str, expire_hours: int = TOKEN_EXPIRY_HOURS) -> str:
    """Create JWT token untuk user."""
    try:
        logger.info(f'Creating JWT token for user_id: {user_id}')
        payload = {
            'sub': user_id,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expire_hours)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        logger.info('Token created successfully')
        return token
    except Exception as e:
        logger.error(f'Error creating JWT token: {str(e)}')
        raise HTTPForbidden('Token creation failed')

def decode_jwt_token(token: str) -> dict:
    """Decode JWT token."""
    try:
        logger.info('Decoding JWT token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        logger.info('Token decoded successfully')
        return payload
    except jwt.ExpiredSignatureError:
        logger.error('Token has expired')
        raise HTTPUnauthorized('Token expired')
    except jwt.InvalidTokenError:
        logger.error('Invalid token')
        raise HTTPUnauthorized('Invalid token')
    except Exception as e:
        logger.error(f'Error decoding JWT token: {str(e)}')
        raise HTTPUnauthorized('Invalid token')

def groupfinder(user_id, request):
    """Function to find user groups/roles."""
    try:
        user = request.dbsession.query(User).filter_by(id=user_id).first()
        if user:
            # Return user's roles as groups
            return ['group:admin'] if user.is_admin else ['group:user']
        return []
    except Exception as e:
        logger.error(f'Error in groupfinder: {str(e)}')
        return []

class JWTAuthenticationPolicy:
    def __init__(self, secret: str):
        """Initialize JWT authentication policy."""
        self.secret = secret
        self.logger = logging.getLogger('momono.security.jwt')
        self.logger.setLevel(logging.INFO)
        
    def unauthenticated_userid(self, request):
        """Get user ID from JWT token."""
        try:
            auth = request.headers.get('Authorization')
            if not auth:
                self.logger.warning('No Authorization header found')
                return None
                
            if not auth.startswith('Bearer '):
                self.logger.warning('Invalid authorization header format')
                return None
                
            token = auth.split(' ')[1]
            if not token:
                self.logger.warning('No token found in authorization header')
                return None
                
            try:
                payload = jwt.decode(token, self.secret, algorithms=['HS256'])
                user_id = payload.get('sub')
                self.logger.info(f'Successfully authenticated user_id: {user_id}')
                return user_id
                
            except jwt.ExpiredSignatureError:
                self.logger.error('Token has expired')
                raise HTTPUnauthorized('Token has expired')
                
            except jwt.InvalidTokenError:
                self.logger.error('Invalid token')
                raise HTTPUnauthorized('Invalid token')
                
            except Exception as e:
                self.logger.error(f'Error decoding JWT token: {str(e)}')
                raise HTTPUnauthorized('Invalid token')
                
        except Exception as e:
            self.logger.error(f'Error in unauthenticated_userid: {str(e)}')
            return None

    def authenticated_userid(self, request):
        """Get authenticated user ID."""
        return self.unauthenticated_userid(request)

    def effective_principals(self, request):
        """Get effective principals (permissions) for user."""
        try:
            user_id = self.authenticated_userid(request)
            if not user_id:
                self.logger.info('No authenticated user')
                return [Everyone]
                
            user = request.dbsession.query(User).filter_by(id=user_id).first()
            if not user:
                self.logger.error(f'User with ID {user_id} not found')
                return [Everyone]
                
            principals = [
                Everyone,
                Authenticated,
                'authenticated',
                'user',
                'view',
                'create',
                'edit',
                'delete',
                'view_dashboard',
                'manage_budgets',
                'manage_users',
                'manage_settings'
            ]
            
            self.logger.info(f'User {user_id} has principals: {principals}')
            return principals
            
        except Exception as e:
            self.logger.error(f'Error getting effective principals: {str(e)}')
            return [Everyone]

    def unauthenticated_userid(self, request):
        try:
            auth = request.headers.get('Authorization')
            if not auth:
                self.logger.warning('No Authorization header found')
                return None
            
            token = auth.split()[1]
            if not token:
                self.logger.warning('Invalid token format')
                return None
            
            try:
                payload = jwt.decode(token, self.secret, algorithms=['HS256'])
                user_id = payload.get('sub')
                self.logger.info(f'Successfully authenticated user_id: {user_id}')
                return user_id
                
            except jwt.ExpiredSignatureError:
                self.logger.error('Token has expired')
                raise HTTPUnauthorized('Token expired')
                
            except jwt.InvalidTokenError:
                self.logger.error('Invalid token')
                raise HTTPUnauthorized('Invalid token')
                
            except Exception as e:
                self.logger.error(f'Error decoding JWT token: {str(e)}')
                raise HTTPUnauthorized('Invalid token')
                
        except Exception as e:
            self.logger.error(f'Error in unauthenticated_userid: {str(e)}')
            return None

    def authenticated_userid(self, request):
        return self.unauthenticated_userid(request)

    def effective_principals(self, request):
        principals = [Everyone]
        user_id = self.authenticated_userid(request)
        if user_id:
            principals.append(Authenticated)
            principals.append(f'user:{user_id}')
            self.logger.info(f'User {user_id} has principals: {principals}')
        return principals