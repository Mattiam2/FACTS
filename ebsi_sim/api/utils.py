"""
from fastapi import Response, APIRouter, Depends, HTTPException

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/create_vp")
def get_vc(did):
"""