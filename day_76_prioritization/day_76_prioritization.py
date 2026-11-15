#!/usr/bin/env python3
"""
Advanced Prioritization Engine
Opportunity Scoring | Weighted Scoring | Economic Prioritization | Strategic Fit

Standard-library-only implementation.

Features:
- Weighted multi-criteria opportunity scoring
- Economic value and expected ROI
- Cost of delay and WSJF prioritization
- Strategic alignment and confidence adjustments
- Risk and implementation complexity
- Dependency validation
- Budget-constrained portfolio selection
- Sensitivity analysis
- Pareto dominance analysis
- JSON persistence and reporting
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

LOGGER = logging.getLogger("prioritization")


class PrioritizationError(Exception):
    """Base exception for prioritization failures."""


class ValidationError(PrioritizationError):
    """Invalid opportunity or scoring configuration."""


class DependencyError(PrioritizationError):
    """Invalid opportunity dependency."""


class OpportunityStatus(str, Enum):
    PROPOSED = "proposed"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    DEFERRED = "deferred"
    REJECTED = "rejected"


class PriorityTier(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class ScoringWeights:
    """Weights for normalized multi-criteria scoring."""

    strategic_fit: float = 0.25
    economic_value: float = 0.25
    customer_value: float = 0.15
    urgency: float = 0.15
    feasibility: float = 0.10
    risk_adjustment: float = 0.10

    def __post_init__(self):
        values = asdict(self)

        if any(not math.isfinite(v) or v < 0 for v in values.values()):
            raise ValidationError("Weights must be finite and non-negative.")

        if not math.isclose(sum(values.values()), 1.0, abs_tol=1e-9):
            raise ValidationError("Scoring weights must sum to 1.0.")


@dataclass
class Opportunity:
    opportunity_id: str
    name: str
    description: str
    strategic_fit: float
    expected_benefit: float
    implementation_cost: float
    customer_value: float
    urgency: float
    feasibility: float
    risk: float
    confidence: float
    cost_of_delay: float
    implementation_effort: float
    dependencies: list[str] = field(default_factory=list)
    mandatory: bool = False
    status: OpportunityStatus = OpportunityStatus.PROPOSED

    def validate(self):
        if not self.opportunity_id.strip() or not self.name.strip():
            raise ValidationError("Opportunity ID and name are required.")

        if self.implementation_cost <= 0:
            raise ValidationError("Implementation cost must be positive.")

        numeric_fields = {
            "strategic_fit": self.strategic_fit,
            "customer_value": self.customer_value,
            "urgency": self.urgency,
            "feasibility": self.feasibility,
            "risk": self.risk,
            "confidence": self.confidence,
        }

        for name, value in numeric_fields.items():
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValidationError(f"{name} must be between 0 and 100.")

        for name, value in {
            "expected_benefit": self.expected_benefit,
            "implementation_cost": self.implementation_cost,
            "cost_of_delay": self.cost_of_delay,
            "implementation_effort": self.implementation_effort,
        }.items():
            if not math.isfinite(value) or value < 0:
                raise ValidationError(f"{name} must be non-negative.")

        if self.implementation_effort <= 0:
            raise ValidationError("Implementation effort must be positive.")

        if not 0 <= self.confidence <= 100:
            raise ValidationError("Confidence must be between 0 and 100.")

        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValidationError("Duplicate dependencies are not allowed.")

        if self.opportunity_id in self.dependencies:
            raise DependencyError("An opportunity cannot depend on itself.")


@dataclass
class OpportunityScore:
    opportunity_id: str
    name: str
    weighted_score: float
    risk_adjusted_score: float
    expected_net_value: float
    expected_roi: float
    cost_of_delay: float
    wsjf_score: float
    strategic_score: float
    tier: PriorityTier
    rank: int = 0


class PrioritizationEngine:

    def __init__(self, weights: ScoringWeights = ScoringWeights()):
        self.weights = weights
        self.opportunities: dict[str, Opportunity] = {}
        self.scores: dict[str, OpportunityScore] = {}

    def add(self, opportunity: Opportunity):
        opportunity.validate()

        if opportunity.opportunity_id in self.opportunities:
            raise ValidationError("Duplicate opportunity ID.")

        self.opportunities[opportunity.opportunity_id] = opportunity

    def validate_dependencies(self):
        for opportunity in self.opportunities.values():
            for dependency in opportunity.dependencies:
                if dependency not in self.opportunities:
                    raise DependencyError(
                        f"{opportunity.opportunity_id} depends on "
                        f"unknown opportunity {dependency}."
                    )

        # Detect circular dependencies using depth-first search.
        visiting = set()
        visited = set()

        def visit(opportunity_id):
            if opportunity_id in visiting:
                raise DependencyError("Circular dependency detected.")

            if opportunity_id in visited:
                return

            visiting.add(opportunity_id)

            for dependency in self.opportunities[
                opportunity_id
            ].dependencies:
                visit(dependency)

            visiting.remove(opportunity_id)
            visited.add(opportunity_id)

        for opportunity_id in self.opportunities:
            visit(opportunity_id)

    @staticmethod
    def calculate_roi(benefit, cost):
        if cost <= 0:
            raise ValidationError("Cost must be positive.")

        return ((benefit - cost) / cost) * 100

    @staticmethod
    def classify(score):
        if score >= 85:
            return PriorityTier.CRITICAL
        if score >= 70:
            return PriorityTier.HIGH
        if score >= 50:
            return PriorityTier.MEDIUM
        return PriorityTier.LOW

    def evaluate(self, opportunity):
        w = self.weights

        # Economic benefit is confidence-adjusted before normalization.
        expected_value = (
            opportunity.expected_benefit
            * opportunity.confidence / 100
        )

        net_value = expected_value - opportunity.implementation_cost

        # Map economic value to a bounded 0-100 score.
        economic_score = max(
            0,
            min(
                100,
                50 + 50 * (
                    net_value /
                    max(opportunity.implementation_cost, 1)
                )
            )
        )

        # Lower risk means a higher risk-adjusted score.
        risk_score = 100 - opportunity.risk

        components = {
            "strategic_fit": opportunity.strategic_fit,
            "economic_value": economic_score,
            "customer_value": opportunity.customer_value,
            "urgency": opportunity.urgency,
            "feasibility": opportunity.feasibility,
            "risk_adjustment": risk_score,
        }

        weighted_score = sum(
            components[name] * weight
            for name, weight in asdict(w).items()
        )

        # Confidence is also applied to the final execution score.
        risk_adjusted_score = (
            weighted_score * opportunity.confidence / 100
        )

        roi = self.calculate_roi(
            expected_value,
            opportunity.implementation_cost
        )

        # WSJF = Cost of Delay / Job Size.
        wsjf = (
            opportunity.cost_of_delay
            / opportunity.implementation_effort
        )

        return OpportunityScore(
            opportunity_id=opportunity.opportunity_id,
            name=opportunity.name,
            weighted_score=round(weighted_score, 2),
            risk_adjusted_score=round(risk_adjusted_score, 2),
            expected_net_value=round(net_value, 2),
            expected_roi=round(roi, 2),
            cost_of_delay=opportunity.cost_of_delay,
            wsjf_score=round(wsjf, 2),
            strategic_score=opportunity.strategic_fit,
            tier=self.classify(risk_adjusted_score),
        )

    def rank(self):
        self.validate_dependencies()

        results = [
            self.evaluate(opportunity)
            for opportunity in self.opportunities.values()
        ]

        results.sort(
            key=lambda x: (
                -x.risk_adjusted_score,
                -x.wsjf_score,
                -x.expected_net_value,
                x.opportunity_id
            )
        )

        for index, score in enumerate(results, start=1):
            score.rank = index
            self.scores[score.opportunity_id] = score

            self.opportunities[
                score.opportunity_id
            ].status = OpportunityStatus.EVALUATED

        return results

    def select_portfolio(self, budget: float):
        """
        Select a feasible portfolio using dependency-aware greedy
        selection. Mandatory opportunities are considered first.

        This is a heuristic, not a globally optimal knapsack solver.
        """

        if not math.isfinite(budget) or budget < 0:
            raise ValidationError("Budget must be non-negative.")

        self.validate_dependencies()
        self.rank()

        selected = set()
        rejected = set()
        remaining = budget

        def closure(opportunity_id):
            result = set()

            def add(item):
                if item in result:
                    return

                result.add(item)

                for dependency in self.opportunities[
                    item
                ].dependencies:
                    add(dependency)

            add(opportunity_id)
            return result

        candidates = sorted(
            self.opportunities.values(),
            key=lambda o: (
                not o.mandatory,
                -self.scores[
                    o.opportunity_id
                ].risk_adjusted_score,
                o.opportunity_id
            )
        )

        for opportunity in candidates:
            required = closure(opportunity.opportunity_id)
            missing = required - selected

            cost = sum(
                self.opportunities[item].implementation_cost
                for item in missing
            )

            if cost <= remaining:
                selected.update(missing)
                remaining -= cost
            elif opportunity.mandatory:
                raise ValidationError(
                    f"Mandatory opportunity {opportunity.opportunity_id} "
                    "and its dependencies exceed the budget."
                )
            else:
                rejected.add(opportunity.opportunity_id)

        # An opportunity is eligible only if all its dependencies
        # are included in the selected portfolio.
        portfolio = [
            self.opportunities[item]
            for item in sorted(selected)
        ]

        return {
            "budget": budget,
            "allocated": round(budget - remaining, 2),
            "remaining": round(remaining, 2),
            "selected": [
                item.opportunity_id for item in portfolio
            ],
            "deferred": sorted(rejected),
            "total_expected_benefit": round(
                sum(
                    item.expected_benefit
                    * item.confidence / 100
                    for item in portfolio
                ),
                2
            ),
            "total_expected_net_value": round(
                sum(
                    item.expected_benefit
                    * item.confidence / 100
                    - item.implementation_cost
                    for item in portfolio
                ),
                2
            )
        }

    def pareto_frontier(self):
        """
        Identify opportunities not dominated simultaneously
        on economic value, strategic fit and feasibility.
        """

        items = list(self.opportunities.values())
        frontier = []

        for candidate in items:
            dominated = False

            for other in items:
                if candidate is other:
                    continue

                at_least_equal = (
                    other.expected_benefit >= candidate.expected_benefit
                    and other.strategic_fit >= candidate.strategic_fit
                    and other.feasibility >= candidate.feasibility
                )

                strictly_better = (
                    other.expected_benefit > candidate.expected_benefit
                    or other.strategic_fit > candidate.strategic_fit
                    or other.feasibility > candidate.feasibility
                )

                if at_least_equal and strictly_better:
                    dominated = True
                    break

            if not dominated:
                frontier.append(candidate.opportunity_id)

        return sorted(frontier)

    def sensitivity_analysis(self, weight_scenarios):
        """Recalculate rankings under alternative scoring weights."""

        results = {}

        for scenario_name, weights in weight_scenarios.items():
            temporary = PrioritizationEngine(weights)

            for opportunity in self.opportunities.values():
                temporary.add(opportunity)

            ranking = temporary.rank()

            results[scenario_name] = [
                item.opportunity_id for item in ranking
            ]

        return results

    def save_report(self, path: str, budget: Optional[float] = None):
        ranking = self.rank()

        report = {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "weights": asdict(self.weights),
            "ranking": [
                asdict(item) for item in ranking
            ],
            "pareto_frontier": self.pareto_frontier(),
        }

        if budget is not None:
            report["portfolio"] = self.select_portfolio(budget)

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Atomic replacement prevents partially written reports.
        temporary = destination.with_suffix(
            destination.suffix + ".tmp"
        )

        temporary.write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8"
        )

        temporary.replace(destination)


def build_sample_engine():
    engine = PrioritizationEngine()

    engine.add(Opportunity(
        opportunity_id="OP-001",
        name="Customer Analytics Platform",
        description="Centralized customer intelligence platform.",
        strategic_fit=95,
        expected_benefit=900000,
        implementation_cost=250000,
        customer_value=90,
        urgency=85,
        feasibility=80,
        risk=25,
        confidence=85,
        cost_of_delay=120000,
        implementation_effort=12
    ))

    engine.add(Opportunity(
        opportunity_id="OP-002",
        name="Cloud Infrastructure Optimization",
        description="Reduce infrastructure operating expenditure.",
        strategic_fit=85,
        expected_benefit=600000,
        implementation_cost=150000,
        customer_value=65,
        urgency=75,
        feasibility=90,
        risk=15,
        confidence=90,
        cost_of_delay=85000,
        implementation_effort=8
    ))

    engine.add(Opportunity(
        opportunity_id="OP-003",
        name="Security Monitoring Modernization",
        description="Improve detection and response capabilities.",
        strategic_fit=100,
        expected_benefit=750000,
        implementation_cost=300000,
        customer_value=80,
        urgency=95,
        feasibility=75,
        risk=20,
        confidence=90,
        cost_of_delay=180000,
        implementation_effort=15,
        mandatory=True
    ))

    engine.add(Opportunity(
        opportunity_id="OP-004",
        name="Mobile Customer Experience",
        description="Improve mobile application usability.",
        strategic_fit=75,
        expected_benefit=450000,
        implementation_cost=120000,
        customer_value=95,
        urgency=70,
        feasibility=85,
        risk=15,
        confidence=80,
        cost_of_delay=70000,
        implementation_effort=7,
        dependencies=["OP-001"]
    ))

    engine.add(Opportunity(
        opportunity_id="OP-005",
        name="Legacy Reporting Automation",
        description="Automate repetitive reporting operations.",
        strategic_fit=60,
        expected_benefit=180000,
        implementation_cost=80000,
        customer_value=50,
        urgency=45,
        feasibility=95,
        risk=10,
        confidence=95,
        cost_of_delay=20000,
        implementation_effort=5
    ))

    return engine


def main():
    engine = build_sample_engine()

    print("\nADVANCED OPPORTUNITY PRIORITIZATION")
    print("=" * 105)

    rankings = engine.rank()

    print(
        f"{'Rank':<6}{'ID':<12}{'Opportunity':<34}"
        f"{'Weighted':>11}{'Adjusted':>11}"
        f"{'ROI %':>11}{'WSJF':>10}{'Tier':>12}"
    )

    for item in rankings:
        print(
            f"{item.rank:<6}"
            f"{item.opportunity_id:<12}"
            f"{item.name[:32]:<34}"
            f"{item.weighted_score:>11.2f}"
            f"{item.risk_adjusted_score:>11.2f}"
            f"{item.expected_roi:>11.2f}"
            f"{item.wsjf_score:>10.2f}"
            f"{item.tier.value:>12}"
        )

    print("\nPARETO FRONTIER")
    print(engine.pareto_frontier())

    print("\nBUDGET-CONSTRAINED PORTFOLIO")
    portfolio = engine.select_portfolio(700000)

    for key, value in portfolio.items():
        print(f"{key}: {value}")

    print("\nSENSITIVITY ANALYSIS")

    alternative_weights = ScoringWeights(
        strategic_fit=0.35,
        economic_value=0.20,
        customer_value=0.15,
        urgency=0.10,
        feasibility=0.10,
        risk_adjustment=0.10
    )

    print(engine.sensitivity_analysis({
        "baseline": engine.weights,
        "strategic_focus": alternative_weights
    }))

    engine.save_report(
        "reports/prioritization_report.json",
        budget=700000
    )

    print("\nReport saved to reports/prioritization_report.json")


if __name__ == "__main__":
    try:
        main()
    except (PrioritizationError, OSError, ValueError) as error:
        LOGGER.error("Execution failed: %s", error)
        raise SystemExit(1)
