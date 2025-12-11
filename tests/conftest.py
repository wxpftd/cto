# pytest configuration and fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


@pytest.fixture(scope="session")
def setup_test_database():
    """Set up test database for the entire test session"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    
    # Create a session for each test
    def get_test_session():
        session = Session()
        try:
            yield session
        finally:
            session.close()
    
    yield get_test_session
    
    # Cleanup after all tests
    Base.metadata.drop_all(bind=engine)