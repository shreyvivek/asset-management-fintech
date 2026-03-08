from collections import Counter
from app.schemas.agents import AgentOutputSchema


class ConsensusService:
    @staticmethod
    def aggregate(agent_outputs: list[dict], debater_output: dict | None) -> dict:
        signals_by_asset: dict[str, list[str]] = {}
        confidences = []
        anchored = 0
        for out in agent_outputs:
            dc = out.get("directional_calls") or []
            for c in dc:
                ac = c.get("asset_class", "other")
                if ac not in signals_by_asset:
                    signals_by_asset[ac] = []
                signals_by_asset[ac].append(c.get("direction") or "neutral")
            confidences.append(out.get("confidence") or 0.5)
            if out.get("evidence_anchors"):
                anchored += 1
        n = len(agent_outputs) or 1
        consensus_strength = sum(confidences) / n
        disagreement = 0.0
        final_signals = {}
        for ac, dirs in signals_by_asset.items():
            if not dirs:
                continue
            c = Counter(dirs)
            most = c.most_common(1)[0][0]
            final_signals[ac] = most
            if len(c) > 1:
                disagreement += 1.0 / len(dirs)
        disagreement_score = min(1.0, disagreement / max(1, len(signals_by_asset)))
        debater_divergence = 0.5 if debater_output else 0.0
        risk_chain_flat = []
        for out in agent_outputs:
            for imp in out.get("implications") or []:
                risk_chain_flat.append(imp)
        return {
            "signals_by_asset": final_signals,
            "consensus_strength": round(consensus_strength, 2),
            "disagreement_score": round(disagreement_score, 2),
            "debater_divergence": debater_divergence,
            "anchored_ratio": round(anchored / n, 2),
            "risk_chain_flat": risk_chain_flat[:10],
        }
