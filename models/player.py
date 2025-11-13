from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class PlayerRegister(BaseModel):
    player_id: str          # unique username / ID (e.g. liam16)
    name: str
    age: int
    position: str           # Midfielder, Striker, etc.
    dominant_foot: Optional[str] = None  # Right, Left, Both
    coach_id: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str           # plain text in request (we hash it before storing)


class PlayerLogin(BaseModel):
    player_id: str
    password: str


class PlayerPublic(BaseModel):
    id: str
    player_id: str
    name: str
    age: int
    position: str
    dominant_foot: Optional[str] = None
    coach_id: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: datetime
