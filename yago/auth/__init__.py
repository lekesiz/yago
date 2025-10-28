"""
YAGO v8.0 - Enterprise SSO
SAML 2.0, OAuth 2.0, LDAP, and Multi-Factor Authentication
"""

from .base import (
    AuthProvider,
    AuthMethod,
    UserRole,
    User,
    Session,
    Token,
    MFAMethod,
    MFAChallenge,
)
from .saml import SAMLProvider
from .oauth import OAuthProvider
from .ldap import LDAPProvider
from .mfa import MFAManager
from .session import SessionManager
from .rbac import RBACManager

__all__ = [
    # Base
    'AuthProvider',
    'AuthMethod',
    'UserRole',
    'User',
    'Session',
    'Token',
    'MFAMethod',
    'MFAChallenge',

    # Providers
    'SAMLProvider',
    'OAuthProvider',
    'LDAPProvider',

    # Core Components
    'MFAManager',
    'SessionManager',
    'RBACManager',
]
