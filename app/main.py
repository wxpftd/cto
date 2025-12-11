from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import health, inbox, planning

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Include routers
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/system", tags=["system"])
app.include_router(inbox.router, prefix=f"{settings.API_V1_STR}/inbox", tags=["inbox"])
app.include_router(planning.router, prefix=f"{settings.API_V1_STR}/planning", tags=["planning"])

@app.get("/")
async def root():
    return {"message": "Hello World"}
