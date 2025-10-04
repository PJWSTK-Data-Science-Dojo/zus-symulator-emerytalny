"""
Modułowe auth dla FastAPI: 1 admin, stateless JWT (bez przechowywania refreshy).

Instalacja:
  pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" pydantic python-dotenv

Zmienne środowiskowe (opcjonalne, plik .env):
  SECRET_KEY=zmien-mnie
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD_HASH=$2b$12$...  # bcrypt

Jeśli ADMIN_PASSWORD_HASH nie jest ustawiony, użyty zostanie fallback dla hasła "secret" (tylko do dev!).

Struktura (dwa pliki w jednym dokumencie):
- auth.py  — logika autoryzacji/JWT (stateless)
- main.py  — FastAPI i endpointy, korzysta z auth.py
"""

# ──────────────────────────────────────────────────────────────────────────────
# auth.py
# ──────────────────────────────────────────────────────────────────────────────
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext

# Konfiguracja z env
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-dev-secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
# Fallback hash dla "secret" (dev only)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_PASSWORD_HASH = pwd_context.hash(ADMIN_PASSWORD) 

def _now():
    return datetime.now(timezone.utc)


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(plain, password_hash)
    except Exception:
        return False


def authenticate_admin(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False
    return verify_password(password, ADMIN_PASSWORD_HASH)


def _base_payload(sub: str, token_type: str, exp_delta: timedelta) -> dict:
    return {
        "sub": sub,
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": int(_now().timestamp()),
        "exp": int((_now() + exp_delta).timestamp()),
    }


def create_access_token(sub: str) -> str:
    payload = _base_payload(sub, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(sub: str) -> str:
    payload = _base_payload(sub, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def refresh_pair(old_refresh_token: str) -> tuple[str, str]:
    """Stateless odświeżenie: weryfikuje ważność/typ i wystawia *nowe* tokeny.
    Brak przechowywania/rotacji = brak możliwości unieważnienia pojedynczego tokena.
    """
    try:
        payload = decode_token(old_refresh_token)
    except JWTError:
        raise ValueError("Nieprawidłowy refresh_token")

    if payload.get("type") != "refresh":
        raise ValueError("Błędny typ tokena (oczekiwano refresh)")

    sub = payload.get("sub")
    if not sub:
        raise ValueError("Brak sub w tokenie")

    return create_access_token(sub), create_refresh_token(sub)


# Dependency do FastAPI
from fastapi import HTTPException, status

def require_admin_from_bearer(token: str) -> str:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Nieprawidłowy typ tokena")
        sub = payload.get("sub")
        if sub != ADMIN_USERNAME:
            raise HTTPException(status_code=403, detail="Brak uprawnień")
        return sub
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token nieprawidłowy lub wygasł")

