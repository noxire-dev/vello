from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from vello.core.models import Base
from vello.core import config

# Determine database URL based on config
if config.IN_MEMORY_DB:
    DATABASE_URL = "sqlite:///:memory:"
    echo_sql = True
else:
    DATABASE_URL = config.DATABASE_URL
    echo_sql = config.DEBUG

engine = create_engine(DATABASE_URL, echo=echo_sql)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

