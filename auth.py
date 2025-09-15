import os
import json
import requests
from typing import Dict, Optional, Any
from urllib.parse import urljoin
import time

class AuthenticationManager:
    """
    Handles various authentication methods for API testing.
    Supports JWT tokens, login flows, API keys, and OAuth.
    """

    def __init__(self):
        self.cached_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.extra_headers: Dict[str, str] = {}
        self.auth_mode = os.getenv("AUTH_MODE", "").lower()
        self._load_extra_headers()

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers based on configured mode.

        Returns:
            Dictionary of headers to include in requests

        Raises:
            RuntimeError: If authentication configuration is invalid or fails
        """
        try:
            if self.auth_mode == "jwt":
                return self._get_jwt_headers()
            elif self.auth_mode == "login":
                return self._get_login_headers()
            elif self.auth_mode == "apikey":
                return self._get_apikey_headers()
            elif self.auth_mode == "basic":
                return self._get_basic_headers()
            elif self.auth_mode == "oauth":
                return self._get_oauth_headers()
            else:
                print("ℹ️  No authentication mode specified, using anonymous access")
                return self.extra_headers.copy()

        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            raise RuntimeError(f"Authentication failed: {str(e)}")

    def _get_jwt_headers(self) -> Dict[str, str]:
        """Handle JWT token authentication."""
        token = os.getenv("JWT_TOKEN")
        if not token:
            raise RuntimeError(
                "AUTH_MODE=jwt requires JWT_TOKEN environment variable\n"
                "Set JWT_TOKEN=your_jwt_token_here"
            )

        print("🔐 Using JWT token authentication")
        headers = {"Authorization": f"Bearer {token}"}
        headers.update(self.extra_headers)
        return headers

    def _get_login_headers(self) -> Dict[str, str]:
        """Handle username/password login flow with token caching."""
        # Check if we have a valid cached token
        if self._is_token_valid():
            print("🔐 Using cached authentication token")
            headers = {"Authorization": f"Bearer {self.cached_token}"}
            headers.update(self.extra_headers)
            return headers

        # Perform fresh login
        print("🔐 Performing login authentication...")
        token = self._perform_login()

        headers = {"Authorization": f"Bearer {token}"}
        headers.update(self.extra_headers)
        return headers

    def _perform_login(self) -> str:
        """Perform login and cache the token."""
        base_url = os.getenv("BASE_URL")
        login_url = os.getenv("LOGIN_URL")
        username = os.getenv("LOGIN_USER")
        password = os.getenv("LOGIN_PASS")

        if not all([base_url, login_url, username, password]):
            raise RuntimeError(
                "AUTH_MODE=login requires all of: BASE_URL, LOGIN_URL, LOGIN_USER, LOGIN_PASS\n"
                "Example:\n"
                "  BASE_URL=https://api.example.com\n"
                "  LOGIN_URL=/auth/login\n"
                "  LOGIN_USER=test@example.com\n"
                "  LOGIN_PASS=password123"
            )

        # Build full login URL
        if login_url.startswith("http"):
            full_login_url = login_url
        else:
            full_login_url = urljoin(base_url.rstrip("/") + "/", login_url.lstrip("/"))

        # Prepare login payload (try common formats)
        login_payloads = [
            {"username": username, "password": password},
            {"email": username, "password": password},
            {"user": username, "pass": password},
            {"login": username, "password": password}
        ]

        # Try different login payload formats
        last_error = None
        for i, payload in enumerate(login_payloads):
            try:
                print(f"   Attempting login format {i+1}/{len(login_payloads)}: {list(payload.keys())}")

                response = requests.post(
                    full_login_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )

                if response.status_code == 200:
                    return self._extract_token_from_response(response)
                elif response.status_code in [400, 401, 422]:
                    # These might indicate wrong payload format, try next one
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    continue
                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if i == len(login_payloads) - 1:  # Last attempt
                    break
                continue

        raise RuntimeError(f"Login failed with all payload formats. Last error: {last_error}")

    def _extract_token_from_response(self, response: requests.Response) -> str:
        """Extract authentication token from login response."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise RuntimeError("Login response is not valid JSON")

        # Try common token field names
        token_fields = [
            "access_token", "token", "jwt", "authToken", "auth_token",
            "accessToken", "bearer", "bearerToken", "bearer_token"
        ]

        # Look for token in root level
        for field in token_fields:
            if field in data and data[field]:
                token = data[field]
                self._cache_token(token, data)
                print(f"✅ Successfully obtained token from field '{field}'")
                return token

        # Look for token in nested objects
        for key, value in data.items():
            if isinstance(value, dict):
                for field in token_fields:
                    if field in value and value[field]:
                        token = value[field]
                        self._cache_token(token, data)
                        print(f"✅ Successfully obtained token from nested field '{key}.{field}'")
                        return token

        # If no token found, show available fields for debugging
        available_fields = self._extract_available_fields(data)
        raise RuntimeError(
            f"No authentication token found in login response.\n"
            f"Available fields: {available_fields}\n"
            f"Expected one of: {', '.join(token_fields)}"
        )

    def _cache_token(self, token: str, response_data: Dict[str, Any]):
        """Cache the authentication token with optional expiration."""
        self.cached_token = token

        # Try to extract expiration time
        expires_in = None
        for field in ["expires_in", "expiresIn", "exp", "expiry"]:
            if field in response_data:
                expires_in = response_data[field]
                break

        if expires_in:
            try:
                # Assume expires_in is seconds from now
                self.token_expires_at = time.time() + int(expires_in) - 60  # 60s buffer
                print(f"   Token cached with {expires_in}s expiration")
            except (ValueError, TypeError):
                print(f"   Token cached (couldn't parse expiration: {expires_in})")
        else:
            # Cache for 1 hour by default
            self.token_expires_at = time.time() + 3600
            print("   Token cached for 1 hour (no expiration info found)")

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid."""
        if not self.cached_token:
            return False

        if self.token_expires_at and time.time() >= self.token_expires_at:
            print("   Cached token expired, will refresh")
            return False

        return True

    def _get_apikey_headers(self) -> Dict[str, str]:
        """Handle API key authentication."""
        api_key = os.getenv("API_KEY")
        api_key_header = os.getenv("API_KEY_HEADER", "X-API-Key")

        if not api_key:
            raise RuntimeError(
                "AUTH_MODE=apikey requires API_KEY environment variable\n"
                "Optional: API_KEY_HEADER (defaults to 'X-API-Key')"
            )

        print(f"🔐 Using API key authentication (header: {api_key_header})")
        headers = {api_key_header: api_key}
        headers.update(self.extra_headers)
        return headers

    def _get_basic_headers(self) -> Dict[str, str]:
        """Handle HTTP Basic authentication."""
        username = os.getenv("BASIC_USER") or os.getenv("LOGIN_USER")
        password = os.getenv("BASIC_PASS") or os.getenv("LOGIN_PASS")

        if not username or not password:
            raise RuntimeError(
                "AUTH_MODE=basic requires BASIC_USER and BASIC_PASS environment variables\n"
                "(or LOGIN_USER and LOGIN_PASS as fallback)"
            )

        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

        print("🔐 Using HTTP Basic authentication")
        headers = {"Authorization": f"Basic {credentials}"}
        headers.update(self.extra_headers)
        return headers

    def _get_oauth_headers(self) -> Dict[str, str]:
        """Handle OAuth 2.0 client credentials flow."""
        client_id = os.getenv("OAUTH_CLIENT_ID")
        client_secret = os.getenv("OAUTH_CLIENT_SECRET")
        token_url = os.getenv("OAUTH_TOKEN_URL")
        scope = os.getenv("OAUTH_SCOPE", "")

        if not all([client_id, client_secret, token_url]):
            raise RuntimeError(
                "AUTH_MODE=oauth requires OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, and OAUTH_TOKEN_URL\n"
                "Optional: OAUTH_SCOPE"
            )

        # Check cached token
        if self._is_token_valid():
            print("🔐 Using cached OAuth token")
            headers = {"Authorization": f"Bearer {self.cached_token}"}
            headers.update(self.extra_headers)
            return headers

        print("🔐 Obtaining OAuth token...")
        token = self._get_oauth_token(client_id, client_secret, token_url, scope)

        headers = {"Authorization": f"Bearer {token}"}
        headers.update(self.extra_headers)
        return headers

    def _get_oauth_token(self, client_id: str, client_secret: str, token_url: str, scope: str) -> str:
        """Get OAuth token using client credentials flow."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }

        if scope:
            payload["scope"] = scope

        try:
            response = requests.post(
                token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            token = data.get("access_token")

            if not token:
                raise RuntimeError(f"No access_token in OAuth response: {data}")

            self._cache_token(token, data)
            print("✅ Successfully obtained OAuth token")
            return token

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OAuth token request failed: {e}")

    def _load_extra_headers(self):
        """Load additional headers from EXTRA_HEADERS environment variable."""
        extra_headers_str = os.getenv("EXTRA_HEADERS", "")
        if extra_headers_str:
            try:
                self.extra_headers = json.loads(extra_headers_str)
                print(f"ℹ️  Loaded {len(self.extra_headers)} extra headers")
            except json.JSONDecodeError:
                print("⚠️  EXTRA_HEADERS is not valid JSON, ignoring")
                self.extra_headers = {}

    def _extract_available_fields(self, data: Any, prefix: str = "", max_depth: int = 3) -> list:
        """Extract available field names from response data for debugging."""
        if max_depth <= 0:
            return []

        fields = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_field = f"{prefix}.{key}" if prefix else key
                fields.append(current_field)

                if isinstance(value, dict) and max_depth > 1:
                    fields.extend(self._extract_available_fields(value, current_field, max_depth - 1))

        return fields

    def refresh_authentication(self):
        """Force refresh of authentication token."""
        print("🔄 Forcing authentication refresh...")
        self.cached_token = None
        self.token_expires_at = None
        return self.get_auth_headers()


# Convenience function for backward compatibility
def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers based on environment configuration.

    Returns:
        Dictionary of headers to include in requests
    """
    auth_manager = AuthenticationManager()
    return auth_manager.get_auth_headers()


if __name__ == "__main__":
    # Test authentication
    print("🧪 Testing authentication...")

    # Mock environment for testing
    os.environ["AUTH_MODE"] = "jwt"
    os.environ["JWT_TOKEN"] = "test.jwt.token"
    os.environ["EXTRA_HEADERS"] = '{"X-Client": "locust-test"}'

    try:
        headers = get_auth_headers()
        print(f"✅ Headers: {headers}")
    except Exception as e:
        print(f"❌ Error: {e}")