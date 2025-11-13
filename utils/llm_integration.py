"""Integration helpers for the training-program language model."""

from __future__ import annotations

import asyncio
import os
from textwrap import dedent
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency in local testing
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled in tests
    OpenAI = None  # type: ignore

_client: Optional["OpenAI"] = None


def _get_client() -> Optional["OpenAI"]:
    """Return a cached OpenAI client if an API key is configured."""

    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None

    _client = OpenAI(api_key=api_key)
    return _client


def _format_markdown_plan(assessment: Dict[str, Any], player: Dict[str, Any]) -> str:
    """Generate a deterministic markdown plan used as a fallback.

    The function looks at a couple of common assessment keys to tailor the
    output.  It keeps the response predictable – critical for testing – while
    still providing helpful content when the live LLM integration is
    unavailable.
    """

    player_name = player.get("player_name", "Player")
    age = player.get("age", "unknown")
    position = player.get("position", "midfielder")
    weaknesses = []

    metrics = assessment.get("metrics", {}) if isinstance(assessment, dict) else {}
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and value < 5:
            weaknesses.append(key.replace("_", " ").title())

    focus = ", ".join(weaknesses) if weaknesses else "overall development"

    template = dedent(
        f"""
        ## Training Plan for {player_name}

        **Age:** {age}  
        **Position:** {position}  
        **Focus Areas:** {focus}

        ### Week 1
        - **Warm-up:** Dynamic mobility and light ball touches
        - **Technical:** First-touch rondos emphasising support angles
        - **Physical:** Acceleration ladders and short sprints
        - **Tactical:** Small-sided possession games with transition cues
        - **Recovery:** Stretching and guided breathing

        ### Week 2
        - **Warm-up:** Coordination ladders with ball control
        - **Technical:** Repetition drills for weaker foot passing
        - **Physical:** Core stability circuits and resisted runs
        - **Tactical:** 6v6 positional play focusing on decision speed
        - **Recovery:** Contrast showers and foam rolling

        ### Week 3
        - **Warm-up:** Quick change-of-direction shuffle series
        - **Technical:** Scenario-based receiving and finishing
        - **Physical:** Aerobic intervals keeping HR in zone 3
        - **Tactical:** Video review & walkthrough of unit roles
        - **Recovery:** Yoga-based mobility session

        ### Week 4
        - **Warm-up:** Technical rondos with pattern play
        - **Technical:** Applied drills linked to match model
        - **Physical:** Power-focused plyometrics with full recovery
        - **Tactical:** Full-team rehearsal and set-piece refinement
        - **Recovery:** Light pool session and nutritional reset
        """
    ).strip()

    return template


async def _call_openai(prompt: str) -> str:
    client = _get_client()
    if client is None:
        raise RuntimeError("OpenAI client is not available")

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(  # type: ignore[arg-type]
        None,
        lambda: client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create individualized soccer training programs for "
                        "youth and elite players."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        ),
    )

    return response.choices[0].message.content


async def generate_training_program(assessment: Dict[str, Any], player: Dict[str, Any]) -> str:
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

    client = _get_client()
    if client is None:
        return _format_markdown_plan(assessment, player)

    try:
        return await _call_openai(prompt)
    except Exception:
        # In testing or when the OpenAI API is unreachable we fall back to a
        # deterministic response so the endpoint remains usable.
        return _format_markdown_plan(assessment, player)

