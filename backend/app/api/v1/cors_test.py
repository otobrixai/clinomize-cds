"""Simple CORS test endpoint"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/cors-test")
async def cors_test():
    return JSONResponse(
        content={"message": "CORS test successful"},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
        }
    )