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
