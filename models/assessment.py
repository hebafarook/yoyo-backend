from pydantic import BaseModel
from typing import Dict, Any

class AssessmentCreate(BaseModel):
    player_id: str
    player_name: str
    age: int
    position: str
    metrics: Dict[str, Any] = {}
