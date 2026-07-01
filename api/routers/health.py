from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "shopmaster",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/")
async def root():
    return {
        "service": "ShopMaster API",
        "version": "2.0.0",
        "docs": "/docs",
        "miniapp": "/miniapp",
        "crm": "/crm",
        "health": "/health"
    }