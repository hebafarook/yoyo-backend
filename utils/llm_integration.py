import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_training_program(assessment: dict, player: dict) -> str:
    player_name = player.get("player_name", "Player")
    age = player.get("age", "unknown")
    position = player.get("position", "midfielder")

    prompt = f"""
You are an elite soccer performance coach.
Create a 4-week training + recovery plan for this player.

Player:
- Name: {player_name}
- Age: {age}
- Position: {position}

Assessment data:
{assessment}

Instructions:
- Show Week 1..4
- Each day: warm-up, technical, physical, tactical, recovery
- Focus on weaknesses from assessment
- Keep it in clean markdown
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create individualized soccer training programs for youth and elite players."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return resp.choices[0].message.content
