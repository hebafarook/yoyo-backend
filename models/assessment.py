from pydantic import BaseModel, Field
from typing import Dict, Any

class AssessmentCreate(BaseModel):
    player_id: str
    player_name: str
    age: int
    position: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
