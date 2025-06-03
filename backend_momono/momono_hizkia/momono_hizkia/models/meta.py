from sqlalchemy import engine_from_config, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register
import logging
import os
from dotenv import load_dotenv

# Konfigurasi logging
logger = logging.getLogger('momono.models')
logger.setLevel(logging.INFO)

# Setup metadata
DBSession = scoped_session(sessionmaker())
Base = declarative_base()
metadata = MetaData()

# Konfigurasi naming convention untuk Alembic
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata.naming_convention = NAMING_CONVENTION
Base.metadata = metadata

def get_engine(settings, prefix='sqlalchemy.'):
    """Get SQLAlchemy engine from settings."""
    try:
        # Log database configuration
        logger.info('Loading database configuration from environment variables')
        
        # Load environment variables
        load_dotenv()
        
        # Get database configuration from env
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        # Log configuration values (except password)
        logger.info(f'Database configuration - User: {db_user}, Host: {db_host}, Port: {db_port}, DB: {db_name}')
        
        # Create database URL
        db_url = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
        # Create engine
        engine = engine_from_config({
            f'{prefix}url': db_url
        })
        logger.info('Database engine created successfully')
        
        # Create all tables if they don't exist
        Base.metadata.create_all(engine)
        logger.info('Database tables created successfully')
        
        return engine
    except Exception as e:
        logger.error(f'Error creating database engine: {str(e)}')
        raise

def get_session_factory(engine):
    """Get SQLAlchemy session factory from engine."""
    try:
        factory = sessionmaker(bind=engine)
        logger.info('Session factory created successfully')
        return factory
    except Exception as e:
        logger.error(f'Error creating session factory: {str(e)}')
        raise

def get_tm_session(session_factory, transaction_manager):
    """Get a SQLAlchemy session instance backed by a transaction."""
    try:
        dbsession = session_factory()
        register(dbsession, transaction_manager=transaction_manager)
        logger.info('Session registered successfully')
        return dbsession
    except Exception as e:
        logger.error(f'Error registering session: {str(e)}')
        raise

def includeme(config):
    """Initialize the model for a Pyramid app.
    Activate this setup using ``config.include('momono_hizkia.momono_hizkia.models')``.
    """
    try:
        settings = config.get_settings()
        settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

        # use pyramid_tm to hook the transaction lifecycle to the request
        config.include('pyramid_tm')

        # use pyramid_retry to retry a request when transient exceptions occur
        config.include('pyramid_retry')

        session_factory = get_session_factory(get_engine(settings))
        config.registry['dbsession_factory'] = session_factory

        # make request.dbsession available for use in Pyramid
        config.add_request_method(
            # r.tm is the transaction manager used by pyramid_tm
            lambda r: get_tm_session(session_factory, r.tm),
            'dbsession',
            reify=True
        )
        logger.info('Models configuration completed successfully')
    except Exception as e:
        logger.error(f'Error in models configuration: {str(e)}')
        raise
