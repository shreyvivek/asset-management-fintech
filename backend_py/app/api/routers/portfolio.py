from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.portfolio import PortfolioProfile, Watchlist, WatchlistItem
from app.services.portfolios.service import PortfolioService

router = APIRouter(prefix="/portfolio-profiles", tags=["portfolio"])


class ProfileCreate(BaseModel):
    name: str
    mandate_persona: str
    organization_id: int | None = None
    asset_class_weights: dict | None = None
    geography_exposure: dict | None = None
    sector_exposures: dict | None = None


class ProfilePatch(BaseModel):
    name: str | None = None
    mandate_persona: str | None = None
    asset_class_weights: dict | None = None
    geography_exposure: dict | None = None
    sector_exposures: dict | None = None


@router.get("")
async def list_profiles(organization_id: int | None = None, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    profiles = await svc.list_profiles(organization_id=organization_id)
    return [{"id": p.id, "name": p.name, "mandate_persona": p.mandate_persona} for p in profiles]


@router.post("")
async def create_profile(body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    p = await svc.create_profile(
        name=body.name,
        mandate_persona=body.mandate_persona,
        organization_id=body.organization_id,
        asset_class_weights=body.asset_class_weights,
        geography_exposure=body.geography_exposure,
        sector_exposures=body.sector_exposures,
    )
    await db.flush()
    return {"id": p.id, "name": p.name}


@router.get("/{profile_id}")
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    p = await svc.get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")
    return {"id": p.id, "name": p.name, "mandate_persona": p.mandate_persona, "asset_class_weights": p.asset_class_weights, "geography_exposure": p.geography_exposure, "sector_exposures": p.sector_exposures}


@router.patch("/{profile_id}")
async def patch_profile(profile_id: int, body: ProfilePatch, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(PortfolioProfile).where(PortfolioProfile.id == profile_id))
    p = r.scalars().first()
    if not p:
        raise HTTPException(404, "Profile not found")
    if body.name is not None:
        p.name = body.name
    if body.mandate_persona is not None:
        p.mandate_persona = body.mandate_persona
    if body.asset_class_weights is not None:
        p.asset_class_weights = body.asset_class_weights
    if body.geography_exposure is not None:
        p.geography_exposure = body.geography_exposure
    if body.sector_exposures is not None:
        p.sector_exposures = body.sector_exposures
    await db.flush()
    return {"id": p.id}

