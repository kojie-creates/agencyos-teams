"""Reusable authentication gate for prototype governed services."""

from dataclasses import dataclass
import hmac


@dataclass(frozen=True)
class AuthResult:
    """Structured authentication decision for gateway callers."""

    authorized: bool
    status: str
    reason_code: str
    required_action: str
    auth_method: str

    def to_dict(self) -> dict:
        return {
            "authorized": self.authorized,
            "status": self.status,
            "reason": self.reason_code,
            "reason_code": self.reason_code,
            "required_action": self.required_action,
            "auth_method": self.auth_method,
        }

    def to_http_status(self) -> int:
        if self.authorized:
            return 200
        if self.status == "NOT_CONFIGURED":
            return 500
        return 401


class OIDCVerifier:
    """Stub verifier boundary for future OIDC integration."""

    def __init__(self, issuer_url: str | None = None, audience: str | None = None):
        self.issuer_url = issuer_url
        self.audience = audience

    def verify_token(self, token: str | None) -> AuthResult:
        return AuthResult(
            authorized=False,
            status="NOT_CONFIGURED",
            reason_code="OIDC_NOT_CONFIGURED",
            required_action="CONFIGURE_OIDC_PROVIDER",
            auth_method="OIDC",
        )


class AuthGate:
    """Validates request authentication before governance or business logic."""

    def __init__(
        self,
        required_api_key: str | None = None,
        oidc_verifier: OIDCVerifier | None = None,
    ):
        self.required_api_key = required_api_key
        self.oidc_verifier = oidc_verifier or OIDCVerifier()

    def verify_api_key(self, supplied_api_key: str | None) -> AuthResult:
        if not self.required_api_key:
            return AuthResult(
                authorized=False,
                status="NOT_CONFIGURED",
                reason_code="API_KEY_NOT_CONFIGURED",
                required_action="SET_AGENCYOS_API_KEY",
                auth_method="API_KEY",
            )

        if hmac.compare_digest(str(supplied_api_key or ""), self.required_api_key):
            return AuthResult(
                authorized=True,
                status="PASS",
                reason_code="AUTHORIZED",
                required_action="NONE",
                auth_method="API_KEY",
            )

        return AuthResult(
            authorized=False,
            status="FAIL",
            reason_code="AUTH_FAILED",
            required_action="CHECK_API_KEY",
            auth_method="API_KEY",
        )

    def verify_oidc_token(self, token: str | None) -> AuthResult:
        return self.oidc_verifier.verify_token(token)
