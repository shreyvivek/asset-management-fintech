from pydantic import BaseModel, Field
from typing import Literal


class DirectionalCall(BaseModel):
    asset_class: str
    direction: Literal["up", "down", "neutral"]
    magnitude: str | None = None


class AssetImpact(BaseModel):
    asset: str
    impact: str


class AgentOutputSchema(BaseModel):
    thesis: str
    directional_calls: list[DirectionalCall] = []
    asset_impacts: list[AssetImpact] = []
    implications: list[str] = []
    confidence: float = Field(ge=0, le=1)
    evidence_anchors: list[str] = []
    risks_caveats: str = ""


class RiskChainNode(BaseModel):
    implication: str
    asset_class: str


class RiskChainSchema(BaseModel):
    first_order: list[RiskChainNode] = []
    second_order: list[RiskChainNode] = []
    third_order: list[RiskChainNode] = []


class DebaterSchema(BaseModel):
    vulnerable_assumptions: list[str] = []
    counter_narrative: str
    historical_counterexample: str = ""
