from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.agents import Simulation, AgentRun, AgentOutput, DebateSummary, ConsensusOutput
from app.models.events import NormalizedEvent

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.get("")
async def list_simulations(limit: int = 50, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Simulation).order_by(Simulation.started_at.desc()).limit(limit))
    sims = r.scalars().all()
    return [{"id": s.id, "normalized_event_id": s.normalized_event_id, "status": s.status, "trigger_reason": s.trigger_reason, "started_at": s.started_at, "completed_at": s.completed_at} for s in sims]


@router.get("/{simulation_id}")
async def get_simulation(simulation_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    sim = r.scalars().first()
    if not sim:
        raise HTTPException(404, "Simulation not found")
    r2 = await db.execute(select(NormalizedEvent).where(NormalizedEvent.id == sim.normalized_event_id))
    ev = r2.scalars().first()
    return {
        "id": sim.id,
        "normalized_event_id": sim.normalized_event_id,
        "event_title": ev.title if ev else None,
        "status": sim.status,
        "trigger_reason": sim.trigger_reason,
        "started_at": sim.started_at,
        "completed_at": sim.completed_at,
    }


@router.get("/{simulation_id}/agents")
async def get_simulation_agents(simulation_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AgentRun).where(AgentRun.simulation_id == simulation_id).order_by(AgentRun.id))
    runs = r.scalars().all()
    out = []
    for run in runs:
        r2 = await db.execute(select(AgentOutput).where(AgentOutput.agent_run_id == run.id))
        out_obj = r2.scalars().first()
        out.append({
            "agent_id": run.agent_id,
            "thesis": out_obj.thesis if out_obj else None,
            "directional_calls": out_obj.directional_calls if out_obj else None,
            "confidence": out_obj.confidence if out_obj else None,
            "is_unanchored": out_obj.is_unanchored if out_obj else None,
        })
    return out


@router.get("/{simulation_id}/consensus")
async def get_simulation_consensus(simulation_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ConsensusOutput).where(ConsensusOutput.simulation_id == simulation_id))
    c = r.scalars().first()
    if not c:
        raise HTTPException(404, "Consensus not found")
    r2 = await db.execute(select(DebateSummary).where(DebateSummary.simulation_id == simulation_id))
    d = r2.scalars().first()
    return {
        "risk_chain": c.risk_chain,
        "signals_by_asset": c.signals_by_asset,
        "consensus_strength": c.consensus_strength,
        "disagreement_score": c.disagreement_score,
        "debater_divergence": c.debater_divergence,
        "anchored_ratio": c.anchored_ratio,
        "debater": {"counter_narrative": d.counter_narrative, "vulnerable_assumptions": d.vulnerable_assumptions, "historical_counterexample": d.historical_counterexample} if d else None,
    }
