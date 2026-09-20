# File: backend/app/main.py
from __future__ import annotations

from collections import Counter
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


StageName = Literal[
    "awareness",
    "consideration",
    "purchase",
    "onboarding",
    "usage",
    "retention",
    "advocacy",
]


class Touchpoint(BaseModel):
    channel: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    sentiment: int = Field(ge=-5, le=5)
    effort: int = Field(ge=1, le=5)
    frequency: int = Field(ge=1, le=5)


class JourneyStage(BaseModel):
    name: StageName
    customer_goal: str = Field(min_length=1, max_length=300)
    customer_actions: list[str] = Field(min_length=1)
    thoughts: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    touchpoints: list[Touchpoint] = Field(default_factory=list)


class JourneyMap(BaseModel):
    persona: str = Field(min_length=1, max_length=200)
    scenario: str = Field(min_length=1, max_length=500)
    stages: list[JourneyStage] = Field(min_length=1)


class JourneyAnalysis(BaseModel):
    average_sentiment: float
    average_effort: float
    total_touchpoints: int
    pain_point_count: int
    opportunity_count: int
    strongest_stage: str | None
    weakest_stage: str | None
    channel_frequency: dict[str, int]


app = FastAPI(
    title="Customer Journey Mapping API",
    version="1.0.0",
    description=(
        "Educational API for creating and analyzing customer journey maps "
        "across awareness, consideration, purchase, onboarding, usage, "
        "retention, and advocacy."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/journeys/analyze", response_model=JourneyAnalysis)
def analyze_journey(journey: JourneyMap) -> JourneyAnalysis:
    if not journey.stages:
        raise HTTPException(status_code=400, detail="At least one stage is required.")

    touchpoints = [
        touchpoint
        for stage in journey.stages
        for touchpoint in stage.touchpoints
    ]

    if touchpoints:
        average_sentiment = round(
            sum(item.sentiment for item in touchpoints) / len(touchpoints), 2
        )
        average_effort = round(
            sum(item.effort for item in touchpoints) / len(touchpoints), 2
        )
    else:
        average_sentiment = 0.0
        average_effort = 0.0

    stage_scores: dict[str, float] = {}

    for stage in journey.stages:
        sentiments = [item.sentiment for item in stage.touchpoints]
        stage_scores[stage.name] = (
            sum(sentiments) / len(sentiments) if sentiments else 0.0
        )

    strongest_stage = max(stage_scores, key=stage_scores.get) if stage_scores else None
    weakest_stage = min(stage_scores, key=stage_scores.get) if stage_scores else None

    channels = Counter(item.channel for item in touchpoints)

    return JourneyAnalysis(
        average_sentiment=average_sentiment,
        average_effort=average_effort,
        total_touchpoints=len(touchpoints),
        pain_point_count=sum(len(stage.pain_points) for stage in journey.stages),
        opportunity_count=sum(len(stage.opportunities) for stage in journey.stages),
        strongest_stage=strongest_stage,
        weakest_stage=weakest_stage,
        channel_frequency=dict(channels),
    )

# File: backend/tests/test_main.py
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_journey() -> dict:
    return {
        "persona": "First-time SaaS buyer",
        "scenario": "Evaluating a project-management platform",
        "stages": [
            {
                "name": "awareness",
                "customer_goal": "Discover a solution",
                "customer_actions": ["Search online"],
                "thoughts": ["Can this solve my problem?"],
                "emotions": ["Curious"],
                "pain_points": ["Too many alternatives"],
                "opportunities": ["Publish educational content"],
                "touchpoints": [
                    {
                        "channel": "Search",
                        "description": "Search engine result",
                        "sentiment": 2,
                        "effort": 2,
                        "frequency": 4,
                    }
                ],
            },
            {
                "name": "purchase",
                "customer_goal": "Choose a product",
                "customer_actions": ["Compare plans", "Start checkout"],
                "thoughts": ["Is the price justified?"],
                "emotions": ["Cautious"],
                "pain_points": ["Pricing is unclear"],
                "opportunities": ["Explain plans clearly"],
                "touchpoints": [
                    {
                        "channel": "Website",
                        "description": "Pricing page",
                        "sentiment": -2,
                        "effort": 4,
                        "frequency": 3,
                    }
                ],
            },
        ],
    }


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_journey() -> None:
    response = client.post("/api/journeys/analyze", json=sample_journey())

    assert response.status_code == 200

    result = response.json()

    assert result["total_touchpoints"] == 2
    assert result["pain_point_count"] == 2
    assert result["opportunity_count"] == 2
    assert result["weakest_stage"] == "purchase"


def test_invalid_sentiment_is_rejected() -> None:
    journey = sample_journey()
    journey["stages"][0]["touchpoints"][0]["sentiment"] = 9

    response = client.post("/api/journeys/analyze", json=journey)

    assert response.status_code == 422


def test_missing_persona_is_rejected() -> None:
    journey = sample_journey()
    del journey["persona"]

    response = client.post("/api/journeys/analyze", json=journey)

    assert response.status_code == 422


