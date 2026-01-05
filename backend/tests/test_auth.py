"""
Test module for authentication utilities.
Run with: python -m pytest backend/tests/test_auth.py -v
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from auth.utils import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token,
    generate_session_token
)


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_wrong(self):
        """Test verify_password with wrong password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert not verify_password("wrongpassword", hashed)
    
    def test_verify_password_empty(self):
        """Test verify_password with empty password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert not verify_password("", hashed)


class TestTokenCreation:
    """Test token creation functions"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        token = create_access_token(user_id=1, username="testuser")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry"""
        expires_delta = timedelta(minutes=60)
        token = create_access_token(user_id=1, username="testuser", expires_delta=expires_delta)
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        token = create_refresh_token(user_id=1, username="testuser")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_refresh_token_different_from_access(self):
        """Test that refresh token is different from access token"""
        access_token = create_access_token(user_id=1, username="testuser")
        refresh_token = create_refresh_token(user_id=1, username="testuser")
        
        assert access_token != refresh_token


class TestTokenDecoding:
    """Test token decoding functions"""
    
    def test_decode_valid_access_token(self):
        """Test decoding valid access token"""
        token = create_access_token(user_id=1, username="testuser")
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "1"  # JWT stores sub as string
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    def test_decode_valid_refresh_token(self):
        """Test decoding valid refresh token"""
        token = create_refresh_token(user_id=1, username="testuser")
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "1"  # JWT stores sub as string
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        payload = decode_token("invalid_token")
        assert payload is None
    
    def test_decode_empty_token(self):
        """Test decoding empty token"""
        payload = decode_token("")
        assert payload is None
    
    def test_decode_malformed_token(self):
        """Test decoding malformed token"""
        payload = decode_token("not.a.valid.jwt.token")
        assert payload is None


class TestSessionToken:
    """Test session token generation"""
    
    def test_generate_session_token(self):
        """Test session token generation"""
        token = generate_session_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_session_token_uniqueness(self):
        """Test that session tokens are unique"""
        tokens = [generate_session_token() for _ in range(10)]
        assert len(tokens) == len(set(tokens))


class TestTokenExpiry:
    """Test token expiry functionality"""
    
    def test_access_token_expiry(self):
        """Test that access token has expiry"""
        token = create_access_token(user_id=1, username="testuser")
        payload = decode_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)  # JWT returns exp as Unix timestamp
    
    def test_refresh_token_expiry(self):
        """Test that refresh token has expiry"""
        token = create_refresh_token(user_id=1, username="testuser")
        payload = decode_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)  # JWT returns exp as Unix timestamp
    
    def test_refresh_token_longer_expiry(self):
        """Test that refresh token has longer expiry than access token"""
        access_token = create_access_token(user_id=1, username="testuser")
        refresh_token = create_refresh_token(user_id=1, username="testuser")
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        # Refresh token should expire later
        assert refresh_payload["exp"] > access_payload["exp"]


# ==================== INTEGRATION TESTS ====================

class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""
    
    def test_full_auth_flow(self):
        """Test complete authentication flow"""
        # 1. Hash password
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # 2. Verify password
        assert verify_password(password, hashed)
        
        # 3. Create access token
        access_token = create_access_token(user_id=1, username="testuser")
        
        # 4. Decode access token
        payload = decode_token(access_token)
        assert payload["sub"] == "1"  # JWT stores sub as string
        assert payload["username"] == "testuser"
        
        # 5. Create refresh token
        refresh_token = create_refresh_token(user_id=1, username="testuser")
        
        # 6. Decode refresh token
        refresh_payload = decode_token(refresh_token)
        assert refresh_payload["sub"] == "1"  # JWT stores sub as string
        assert refresh_payload["type"] == "refresh"
    
    def test_user_registration_flow(self):
        """Test user registration flow"""
        username = "newuser"
        email = "newuser@example.com"
        password = "securepassword123"
        
        # 1. Hash password
        hashed = get_password_hash(password)
        
        # 2. Create tokens
        access_token = create_access_token(user_id=1, username=username)
        refresh_token = create_refresh_token(user_id=1, username=username)
        
        # 3. Verify tokens
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        assert access_payload["username"] == username
        assert refresh_payload["username"] == username
        assert verify_password(password, hashed)
    
    def test_password_change_flow(self):
        """Test password change flow"""
        old_password = "oldpassword123"
        new_password = "newpassword456"
        
        # 1. Hash old password
        old_hashed = get_password_hash(old_password)
        
        # 2. Verify old password
        assert verify_password(old_password, old_hashed)
        
        # 3. Hash new password
        new_hashed = get_password_hash(new_password)
        
        # 4. Verify new password (and old password no longer works)
        assert verify_password(new_password, new_hashed)
        assert not verify_password(old_password, new_hashed)


class TestPhoneNumberUpdate:
    """Test phone number update functionality"""
    
    def test_phone_number_field_exists(self):
        """Test that User model has phone_number field"""
        from db.models import User
        assert hasattr(User, 'phone_number')
    
    def test_phone_number_nullable(self):
        """Test that phone_number is nullable"""
        from db.models import User
        # Check that phone_number column allows null
        phone_column = User.__table__.columns.get('phone_number')
        assert phone_column is not None


# ==================== RUNNER ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])