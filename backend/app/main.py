from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import router as api_v1_router, ws_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Document Analyzer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}

app.include_router(api_v1_router)
app.include_router(ws_router)
