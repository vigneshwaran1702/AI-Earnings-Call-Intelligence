from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────
    init_db()
    print("\n✦  Finosauras Intelligence — database initialized")
    print("✦  Docs:  http://127.0.0.1:8000/docs")
    print("✦  API:   http://127.0.0.1:8000/api/companies\n")
    yield
    # ── Shutdown ───────────────────────────────────────────────────
    print("\n✦  Finosauras API shutting down\n")


app = FastAPI(
    title="Finosauras Intelligence",
    description=(
        "AI-powered Indian Earnings Call Intelligence Platform — "
        "monitors NSE & BSE corporate filings, extracts earnings-call "
        "transcripts, and generates structured AI summaries."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (allow React dev server) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────
app.include_router(api_router)
app.include_router(ws_router)


# ── Root redirect ──────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "app": "Finosauras Intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "companies":    "/api/companies",
            "transcripts":  "/api/transcripts",
            "stats":        "/api/stats",
            "health":       "/api/health",
            "websocket":    "ws://127.0.0.1:8000/ws/pipeline",
        },
    }

