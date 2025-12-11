from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import health

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Include routers
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/system", tags=["system"])

@app.get("/")
async def root():
    return {"message": "Hello World"}
