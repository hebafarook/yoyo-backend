from pydantic import BaseModel, Field
from typing import List, Optional


class AssessmentMetrics(BaseModel):
    sprint_30m: float
    agility_test: float
    reaction_time_ms: float
    beep_test_level: float
    ball_control_score: float
    passing_accuracy_pct: float
    overall_score: float


class AssessmentCreate(BaseModel):
    player_id: str
    player_name: str
    age: int
    position: str
    metrics: AssessmentMetrics
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
