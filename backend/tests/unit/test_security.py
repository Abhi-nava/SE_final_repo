import os
import sys
from datetime import datetime, timedelta, timezone

# Setup paths before imports
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from utils.security import PasswordResetToken  # noqa: E402
from utils.security import (
    TwoFactorAuthToken,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_2fa_token,
    generate_otp,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_creates_sha256_hash(self):
        password = "testpassword123"
        hashed = hash_password(password)

        # SHA-256 hash should be 64 characters (hex)
        assert len(hashed) == 64
        assert hashed.isalnum()

    def test_hash_password_is_deterministic(self):
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Same password should produce same hash
        assert hash1 == hash2

    def test_verify_password_success(self):
        password = "correctpassword"
        hashed = hash_password(password)

        # verify_password expects both to be hashed already
        assert verify_password(hashed, hashed) is True

    def test_verify_password_failure(self):
        password1 = "correctpassword"
        password2 = "wrongpassword"
        hashed1 = hash_password(password1)
        hashed2 = hash_password(password2)

        assert verify_password(hashed2, hashed1) is False

    def test_hash_different_passwords_produce_different_hashes(self):
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")

        assert hash1 != hash2


class TestTokenGeneration:
    """Test JWT token creation and validation"""

    def test_create_access_token_default_expiry(self):
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    def test_create_access_token_custom_expiry(self):
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=10)
        token = create_access_token(data, expires_delta)

        decoded = decode_token(token)
        assert decoded is not None

        # Check expiry is roughly 10 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (exp_time - now).total_seconds()

        # Should be around 600 seconds (10 minutes), allow some tolerance
        assert 595 < diff < 605

    def test_create_refresh_token(self):
        data = {"sub": "user456", "email": "refresh@example.com"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user456"
        assert decoded["email"] == "refresh@example.com"

    def test_decode_valid_token(self):
        data = {"sub": "user789", "role": "customer"}
        token = create_access_token(data)

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user789"
        assert decoded["role"] == "customer"

    def test_decode_invalid_token(self):
        invalid_token = "invalid.token.string"
        decoded = decode_token(invalid_token)

        assert decoded is None

    def test_decode_expired_token(self):
        data = {"sub": "user999"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)

        # Should return None for expired token
        decoded = decode_token(token)
        assert decoded is None


class TestOTPGeneration:
    """Test OTP generation"""

    def test_generate_otp_format(self):
        otp = generate_otp()

        # OTP should be 6 digits
        assert isinstance(otp, str)
        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_range(self):
        otp = generate_otp()
        otp_int = int(otp)

        # OTP should be between 100000 and 999999
        assert 100000 <= otp_int <= 999999

    def test_generate_otp_uniqueness(self):
        # Generate multiple OTPs and check they're not all the same
        otps = {generate_otp() for _ in range(100)}

        # Should have some variety (not all identical)
        assert len(otps) > 1


class TestTwoFactorAuthToken:
    """Test 2FA token generation and verification"""

    def test_create_temp_token(self):
        user_id = "user123"
        email = "test@example.com"

        token = TwoFactorAuthToken.create_temp_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_temp_token_valid(self):
        user_id = "user456"
        email = "verify@example.com"

        token = TwoFactorAuthToken.create_temp_token(user_id, email)
        payload = TwoFactorAuthToken.verify_temp_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "2fa_temp"
        assert "otp" in payload
        assert len(payload["otp"]) == 6

    def test_verify_temp_token_invalid(self):
        invalid_token = "invalid.token"
        payload = TwoFactorAuthToken.verify_temp_token(invalid_token)

        assert payload is None

    def test_verify_temp_token_wrong_type(self):
        # Create a regular access token (not 2fa_temp type)
        regular_token = create_access_token({"sub": "user", "type": "access"})
        payload = TwoFactorAuthToken.verify_temp_token(regular_token)

        assert payload is None

    def test_verify_otp_correct(self):
        token = TwoFactorAuthToken.create_temp_token("user789", "otp@example.com")
        payload = TwoFactorAuthToken.verify_temp_token(token)
        correct_otp = payload["otp"]

        result = TwoFactorAuthToken.verify_otp(token, correct_otp)
        assert result is True

    def test_verify_otp_incorrect(self):
        token = TwoFactorAuthToken.create_temp_token("user999", "wrong@example.com")

        result = TwoFactorAuthToken.verify_otp(token, "000000")
        assert result is False

    def test_verify_otp_invalid_token(self):
        result = TwoFactorAuthToken.verify_otp("invalid.token", "123456")
        assert result is False

    def test_temp_token_expiry(self):
        # Create token with very short expiry
        token = TwoFactorAuthToken.create_temp_token(
            "user", "test@example.com", expires_in=1
        )

        # Wait for token to expire
        import time

        time.sleep(2)

        payload = TwoFactorAuthToken.verify_temp_token(token)
        assert payload is None


class TestPasswordResetToken:
    """Test password reset token functionality"""

    def test_create_temp_reset_token(self):
        email = "reset@example.com"
        token = PasswordResetToken.create_temp_token(email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_temp_reset_token_valid(self):
        email = "verify-reset@example.com"
        token = PasswordResetToken.create_temp_token(email)

        payload = PasswordResetToken.verify_temp_token(token)

        assert payload is not None
        assert payload["email"] == email
        assert payload["type"] == "reset_temp"
        assert "otp" in payload
        assert len(payload["otp"]) == 6

    def test_verify_temp_reset_token_invalid(self):
        invalid_token = "invalid.reset.token"
        payload = PasswordResetToken.verify_temp_token(invalid_token)

        assert payload is None

    def test_verify_reset_otp_correct(self):
        token = PasswordResetToken.create_temp_token("reset-otp@example.com")
        payload = PasswordResetToken.verify_temp_token(token)
        correct_otp = payload["otp"]

        result = PasswordResetToken.verify_otp(token, correct_otp)
        assert result is True

    def test_verify_reset_otp_incorrect(self):
        token = PasswordResetToken.create_temp_token("wrong-otp@example.com")

        result = PasswordResetToken.verify_otp(token, "999999")
        assert result is False

    def test_create_reset_session_token(self):
        email = "session@example.com"
        token = PasswordResetToken.create_reset_session_token(email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_reset_session_token_valid(self):
        email = "valid-session@example.com"
        token = PasswordResetToken.create_reset_session_token(email)

        payload = PasswordResetToken.verify_reset_session_token(token)

        assert payload is not None
        assert payload["email"] == email
        assert payload["type"] == "reset_session"

    def test_verify_reset_session_token_invalid(self):
        invalid_token = "invalid.session.token"
        payload = PasswordResetToken.verify_reset_session_token(invalid_token)

        assert payload is None

    def test_verify_reset_session_token_wrong_type(self):
        # Create temp token and try to verify as session token
        temp_token = PasswordResetToken.create_temp_token("wrong-type@example.com")
        payload = PasswordResetToken.verify_reset_session_token(temp_token)

        assert payload is None

    def test_reset_token_expiry(self):
        # Create token with very short expiry
        token = PasswordResetToken.create_temp_token("expire@example.com", expires_in=1)

        # Wait for token to expire
        import time

        time.sleep(2)

        payload = PasswordResetToken.verify_temp_token(token)
        assert payload is None


class TestGenerate2FAToken:
    """Test 2FA token generation utility"""

    def test_generate_2fa_token_format(self):
        token = generate_2fa_token()

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_2fa_token_uniqueness(self):
        tokens = {generate_2fa_token() for _ in range(10)}

        # All tokens should be unique
        assert len(tokens) == 10

    def test_generate_2fa_token_url_safe(self):
        token = generate_2fa_token()

        # Should not contain problematic characters
        assert "/" not in token or "_" in token  # URL-safe base64
