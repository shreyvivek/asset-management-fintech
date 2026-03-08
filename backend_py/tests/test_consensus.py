from app.services.agents.consensus import ConsensusService


def test_aggregate_empty():
    out = ConsensusService.aggregate([], None)
    assert "signals_by_asset" in out
    assert out["consensus_strength"] == 0
    assert "disagreement_score" in out


def test_aggregate_single_agent():
    agents = [
        {"thesis": "Rates up", "directional_calls": [{"asset_class": "rates", "direction": "up"}], "confidence": 0.8, "evidence_anchors": ["CME"]},
    ]
    out = ConsensusService.aggregate(agents, {})
    assert out["signals_by_asset"].get("rates") == "up"
    assert out["consensus_strength"] == 0.8
    assert out["anchored_ratio"] == 1.0


def test_aggregate_disagreement():
    agents = [
        {"directional_calls": [{"asset_class": "rates", "direction": "up"}], "confidence": 0.7, "evidence_anchors": []},
        {"directional_calls": [{"asset_class": "rates", "direction": "down"}], "confidence": 0.6, "evidence_anchors": []},
    ]
    out = ConsensusService.aggregate(agents, {"counter_narrative": "Maybe wrong"})
    assert "rates" in out["signals_by_asset"]
    assert out["disagreement_score"] >= 0
    assert out["debater_divergence"] == 0.5
