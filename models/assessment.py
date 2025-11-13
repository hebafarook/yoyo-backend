from pydantic import BaseModel
from typing import Dict, Any, Optional

class AssessmentCreate(BaseModel):
    player_id: str
    player_name: str
    age: int
    position: str
    metrics: Optional[Dict[str, Any]] = None
