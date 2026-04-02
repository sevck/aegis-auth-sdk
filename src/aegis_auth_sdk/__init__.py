"""
Aegis Auth SDK - WebAuthn 无密码认证平台 Python SDK
"""

from .client import AegisClient
from .response import AegisResponse
from .exceptions import AegisError

__version__ = "0.0.9"
__all__ = ["AegisClient", "AegisResponse", "AegisError"]
