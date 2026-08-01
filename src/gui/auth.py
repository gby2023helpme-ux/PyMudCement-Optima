import json
import hashlib
import os
from datetime import datetime
from typing import Optional

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "users.json",
)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def create_user(username: str, password: str, full_name: str = "") -> bool:
    users = _load_users()
    username = username.strip()
    if username in users:
        return False
    users[username] = {
        "password_hash": _hash_password(password),
        "full_name": full_name.strip() or username,
        "created": datetime.now().isoformat(),
    }
    _save_users(users)
    return True


def authenticate(username: str, password: str) -> Optional[str]:
    users = _load_users()
    username = username.strip()
    user = users.get(username)
    if user and user.get("password_hash") == _hash_password(password):
        return user.get("full_name", username)
    return None
