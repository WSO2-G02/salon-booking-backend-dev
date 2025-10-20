"""
Unit tests for User Service.
Demonstrates testing approach for microservices.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user_service.core.main import app
from user_service.core import models
from common.database import get_db, Base
from common.security import verify_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPassword123",
            "full_name": "Test User",
            "phone": "+1234567890"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data  # Password should not be returned
        assert "id" in data
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "StrongPassword123",
            "full_name": "User One"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        user_data["username"] = "user2"  # Different username
        response2 = client.post("/api/v1/register", json=user_data)
        assert response2.status_code == 409
        assert "Email already registered" in response2.json()["detail"]
    
    def test_register_weak_password(self):
        """Test registration with weak password"""
        user_data = {
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "weak",  # Too short, no uppercase, no digits
            "full_name": "Weak User"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 422  # Validation error

class TestUserAuthentication:
    """Test user authentication functionality"""
    
    @pytest.fixture
    def registered_user(self):
        """Create a registered user for authentication tests"""
        user_data = {
            "email": "auth@example.com",
            "username": "authuser",
            "password": "AuthPassword123",
            "full_name": "Auth User"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 201
        return user_data
    
    def test_login_success(self, registered_user):
        """Test successful login"""
        login_data = {
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
        
        response = client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_login_invalid_credentials(self, registered_user):
        """Test login with invalid credentials"""
        login_data = {
            "username": registered_user["username"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == 401

class TestPasswordSecurity:
    """Test password security functions"""
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        from common.security import get_password_hash, verify_password
        
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        # Hash should not equal original password
        assert hashed != password
        
        # Should be able to verify correct password
        assert verify_password(password, hashed) is True
        
        # Should reject incorrect password
        assert verify_password("wrongpassword", hashed) is False

class TestProtectedEndpoints:
    """Test endpoints that require authentication"""
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for protected endpoint tests"""
        # Register and login user
        user_data = {
            "email": "protected@example.com",
            "username": "protecteduser",
            "password": "ProtectedPassword123",
            "full_name": "Protected User"
        }
        
        client.post("/api/v1/register", json=user_data)
        
        login_response = client.post("/api/v1/login", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_profile_success(self, auth_headers):
        """Test getting user profile with valid token"""
        response = client.get("/api/v1/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "protecteduser"
        assert data["email"] == "protected@example.com"
    
    def test_get_profile_no_token(self):
        """Test getting user profile without token"""
        response = client.get("/api/v1/profile")
        assert response.status_code == 403  # Forbidden
    
    def test_get_profile_invalid_token(self):
        """Test getting user profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/profile", headers=headers)
        assert response.status_code == 401  # Unauthorized

# Integration test example
class TestAppointmentBookingFlow:
    """Integration test for appointment booking workflow"""
    
    def test_complete_booking_flow(self):
        """
        Test the complete appointment booking flow across services.
        This is a simplified integration test.
        """
        # 1. Register user
        user_data = {
            "email": "booking@example.com",
            "username": "bookinguser",
            "password": "BookingPassword123",
            "full_name": "Booking User"
        }
        
        register_response = client.post("/api/v1/register", json=user_data)
        assert register_response.status_code == 201
        
        # 2. Login user
        login_response = client.post("/api/v1/login", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        # 3. In a real integration test, you would:
        # - Create a service in Service Management Service
        # - Create a staff member in Staff Management Service
        # - Check availability
        # - Book appointment in Appointment Service
        # - Verify notification was sent
        
        # This demonstrates the testing approach for microservices integration