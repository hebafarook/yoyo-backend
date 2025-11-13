import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import app  # noqa: E402
from utils.database import db  # noqa: E402


async def _prepare_data():
    await db.assessments.insert_one(
        {
            "player_id": "p1",
            "player_name": "Jordan",
            "age": 16,
            "position": "midfielder",
            "metrics": {"speed": 4, "vision": 7},
            "created_at": datetime.utcnow() - timedelta(days=1),
        }
    )
    await db.assessments.insert_one(
        {
            "player_id": "p1",
            "player_name": "Jordan",
            "age": 16,
            "position": "midfielder",
            "metrics": {"speed": 3, "vision": 6},
            "created_at": datetime.utcnow(),
        }
    )


def test_generate_program_returns_markdown_when_llm_unavailable():
    asyncio.run(_prepare_data())

    client = TestClient(app)
    response = client.post("/api/programs/generate", params={"player_id": "p1"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["player_id"] == "p1"
    program = payload["program"]

    assert "## Training Plan for Jordan" in program
    assert "Week 1" in program
    assert "Focus Areas" in program
