import hashlib
import secrets
from datetime import datetime
from typing import Optional

from utils.database import db


def hash_password(password: str) -> str:
    """
    Simple SHA256 hash. Good enough for now; later you can upgrade
    to bcrypt/argon2 with passlib.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def create_session(player_id: str) -> str:
    """
    Create a session token stored in Mongo. Returns the token string.
    """
    token = secrets.token_hex(32)
    await db.sessions.insert_one(
        {
            "token": token,
            "player_id": player_id,
            "created_at": datetime.utcnow(),
        }
    )
    return token


async def get_player_by_token(token: str) -> Optional[dict]:
    """
    Look up the player document from a session token.
    """
    if not token:
        return None

    session = await db.sessions.find_one({"token": token})
    if not session:
        return None

    player = await db.players.find_one({"player_id": session["player_id"]})
    return player
