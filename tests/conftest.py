"""
conftest.py - Test Configuration File
=====================================

This file is automatically loaded by pytest. It contains "fixtures" which are
reusable test components. Think of fixtures as setup/teardown functions that
prepare your test environment.

What are fixtures?
- They prepare data or objects before tests run
- They clean up after tests finish
- They make tests reusable and maintainable

Why do we need them?
- To set up a test database (not your real database!)
- To create a test Flask app
- To provide test users and data
"""
from unittest.mock import MagicMock

import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set test environment variables BEFORE importing anything else
# This ensures the app uses an in-memory database for testing
os.environ['DB_URI'] = 'sqlite:///:memory:'
os.environ['FLASK_KEY'] = 'test-secret-key'


# ===== FIXTURE: Test App =====
@pytest.fixture(scope="session")
def app():
    """
    Creates a Flask app for testing.
    
    This fixture:
    - Creates a test version of your app
    - Uses an in-memory SQLite database (fast, no file needed)
    - Returns the app for tests to use
    
    The 'yield' keyword is important:
    - Everything before yield: SETUP (runs before test)
    - Everything after yield: TEARDOWN (runs after test)
    
    scope="session" means the app is created once for all tests
    """
    # Import after setting env vars so it uses test config
    from routes import create_app
    from extensions import db
    
    # Create the app (it will use test DB_URI from env var)
    app = create_app()
    
    # Override config to ensure test mode
    app.config['TESTING'] = True
    
    # Create all tables in the test database
    with app.app_context():
        db.create_all()
    
    yield app  # This is where the test runs
    
    # Cleanup after all tests
    with app.app_context():
        db.session.remove()
        db.drop_all()


# ===== FIXTURE: Test Client =====
@pytest.fixture
def client(app):
    """
    Creates a test client for making HTTP requests.
    
    This allows tests to simulate HTTP requests like:
    - client.get('/some-route')
    - client.post('/login', json={...})
    
    Think of this as a "browser" for your tests.
    """
    return app.test_client()


# ===== FIXTURE: Test Database Session =====
@pytest.fixture
def db_session(app):
    """
    Provides a database session for tests.
    
    This fixture gives tests access to the database so they can:
    - Create test users
    - Query data
    - Add test data
    
    Deletes all data from tables before each test to ensure isolation.
    """
    from extensions import db
    from models import User, SectorManagement, Group, AuthorityLevel
    from models.users_and_authentication import UserToken
    
    with app.app_context():
        # Delete all data before each test
        try:
            db.session.query(UserToken).delete()
            db.session.query(User).delete()
            db.session.query(SectorManagement).delete()
            db.session.query(Group).delete()
            db.session.query(AuthorityLevel).delete()
            db.session.commit()
        except:
            db.session.rollback()
        
        yield db


# ===== FIXTURE: Test User =====
@pytest.fixture
def test_user(db_session):
    """
    Creates a test user in the database.
    
    This fixture creates a user that tests can use. It's reusable
    across multiple tests, saving you from creating users manually.
    """
    # Import models here to avoid circular imports
    from models import User, SectorManagement, Group, AuthorityLevel
    from decimal import Decimal
    
    # First create required related objects
    sector = SectorManagement(
        name="Test Sector",
        from_x_axis=Decimal('0.0'),
        to_x_axis=Decimal('1.0'),
        from_y_axis=Decimal('0.0'),
        to_y_axis=Decimal('1.0'),
        authority_level_id=1
    )
    db_session.session.add(sector)
    db_session.session.flush()
    
    group = Group(group_name="Test Group")
    db_session.session.add(group)
    db_session.session.flush()
    
    auth_level = AuthorityLevel(description="Test Authority")
    db_session.session.add(auth_level)
    db_session.session.flush()
    
    # Create the user with group_id=3 for register route access
    user = User(
        emp_code="12345678",
        emp_name="Test User",
        username="testuser",
        userpassword="hashed_password_here",
        sector_management_id=sector.id,
        group_id=3,  # Group 3 has permission to register users
        authority_level_id=auth_level.id,
        is_active=True
    )
    db_session.session.add(user)
    db_session.session.commit()
    
    return user


# ===== FIXTURE: Auth Headers =====
@pytest.fixture
def auth_headers(app, test_user):
    """
    Creates authentication headers for protected routes.
    
    Many routes require JWT tokens. This fixture creates a valid token
    and returns it in the proper format for test requests.
    """
    from flask_jwt_extended import create_access_token
    
    with app.app_context():
        # Create a JWT token for the test user
        token = create_access_token(identity=str(test_user.user_id))
        
        # Return headers with the token
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def mock_manager():
    manager = MagicMock()

    manager.user_id = 5
    manager.tokens = [
        MagicMock(token="abc123"),
        MagicMock(token="xyz456")
    ]

    return manager