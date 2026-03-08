import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers import get_llm_provider
from app.prompts.templates import AGENT_SYSTEM_TEMPLATE, DEBATER_PROMPT
from app.models.agents import Simulation, SimulationInput, AgentRun, AgentOutput, EvidenceAnchor, DebateSummary, ConsensusOutput
from app.models.events import NormalizedEvent
from app.services.agents.registry import AGENT_REGISTRY, get_agent_focus
from app.services.agents.risk_chain import RiskChainService
from app.services.agents.consensus import ConsensusService
from app.services.memory.service import MemoryService


def _parse_agent_json(content: str) -> dict:
    try:
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "thesis": content[:500] if content else "No parseable output.",
            "directional_calls": [],
            "asset_impacts": [],
            "implications": [],
            "confidence": 0.5,
            "evidence_anchors": ["Unanchored"],
            "risks_caveats": "Output could not be validated.",
        }


class AgentRunner:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_provider()
        self.risk_chain_svc = RiskChainService()
        self.consensus_svc = ConsensusService()
        self.memory_svc = MemoryService(db)

    async def run_simulation(
        self,
        normalized_event_id: int,
        portfolio_profile_id: int | None = None,
        trigger_reason: str = "manual",
    ) -> int:
        r = await self.db.execute(select(NormalizedEvent).where(NormalizedEvent.id == normalized_event_id))
        event = r.scalars().first()
        if not event:
            return 0
        sim = Simulation(
            normalized_event_id=normalized_event_id,
            portfolio_profile_id=portfolio_profile_id,
            trigger_reason=trigger_reason,
            status="running",
        )
        self.db.add(sim)
        await self.db.flush()
        self.db.add(SimulationInput(simulation_id=sim.id, input_type="event", payload={"event_id": normalized_event_id}))
        risk_chain = await self.risk_chain_svc.generate(event.title, event.summary)
        analogues = await self.memory_svc.retrieve_analogues(normalized_event_id, top_k=3, simulation_id=sim.id)
        analogue_text = "\n".join([f"- {a.title} → {a.outcome_24h or 'N/A'}" for a in analogues])
        context = f"Event: {event.title}\nSummary: {event.summary or ''}\n\nHistorical analogues:\n{analogue_text}\n\nRisk chain: {json.dumps(risk_chain)}"
        agent_outputs = []
        for agent in AGENT_REGISTRY:
            run = AgentRun(simulation_id=sim.id, agent_id=agent["id"], status="running")
            self.db.add(run)
            await self.db.flush()
            prompt = AGENT_SYSTEM_TEMPLATE.format(
                agent_name=agent["name"],
                focus=agent["focus"],
            )
            content = await self.llm.chat([
                {"role": "system", "content": prompt},
                {"role": "user", "content": context},
            ])
            parsed = _parse_agent_json(content)
            is_unanchored = not (parsed.get("evidence_anchors") and len(parsed["evidence_anchors"]) > 0)
            out = AgentOutput(
                agent_run_id=run.id,
                thesis=parsed.get("thesis"),
                directional_calls=parsed.get("directional_calls"),
                asset_impacts=parsed.get("asset_impacts"),
                implications=parsed.get("implications"),
                confidence=parsed.get("confidence", 0.5),
                risks_caveats=parsed.get("risks_caveats"),
                raw_response=content[:4000],
                is_unanchored=is_unanchored,
            )
            self.db.add(out)
            await self.db.flush()
            for anchor in parsed.get("evidence_anchors") or []:
                self.db.add(EvidenceAnchor(agent_output_id=out.id, anchor_text=str(anchor)[:512]))
            agent_outputs.append(parsed)
        theses_summary = " ".join([o.get("thesis", "")[:200] for o in agent_outputs])
        debater_prompt = DEBATER_PROMPT.format(title=event.title, theses_summary=theses_summary)
        debater_content = await self.llm.chat([{"role": "user", "content": debater_prompt}])
        try:
            debater_parsed = _parse_agent_json(debater_content)
            if "counter_narrative" not in debater_parsed:
                debater_parsed["counter_narrative"] = debater_content[:500]
            if "vulnerable_assumptions" not in debater_parsed:
                debater_parsed["vulnerable_assumptions"] = []
            if "historical_counterexample" not in debater_parsed:
                debater_parsed["historical_counterexample"] = ""
        except Exception:
            debater_parsed = {
                "vulnerable_assumptions": [],
                "counter_narrative": debater_content[:500],
                "historical_counterexample": "See counter_narrative.",
            }
        self.db.add(DebateSummary(
            simulation_id=sim.id,
            debater_thesis=debater_parsed.get("counter_narrative"),
            vulnerable_assumptions=debater_parsed.get("vulnerable_assumptions"),
            counter_narrative=debater_parsed.get("counter_narrative"),
            historical_counterexample=debater_parsed.get("historical_counterexample"),
        ))
        consensus = self.consensus_svc.aggregate(agent_outputs, debater_parsed)
        self.db.add(ConsensusOutput(
            simulation_id=sim.id,
            risk_chain=risk_chain,
            signals_by_asset=consensus.get("signals_by_asset"),
            consensus_strength=consensus.get("consensus_strength"),
            disagreement_score=consensus.get("disagreement_score"),
            debater_divergence=consensus.get("debater_divergence"),
            anchored_ratio=consensus.get("anchored_ratio"),
        ))
        sim.status = "completed"
        sim.completed_at = datetime.utcnow()
        await self.db.commit()
        return sim.id
