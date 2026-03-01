from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import acc, procore, hcss, canonical

app = FastAPI(title="Unified Ops Mock Server MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(acc.router, prefix="/mock/acc", tags=["mock-acc"])
app.include_router(procore.router, prefix="/mock/procore", tags=["mock-procore"])
app.include_router(hcss.router, prefix="/mock/hcss", tags=["mock-hcss"])
app.include_router(canonical.router, prefix="/api", tags=["canonical"])

@app.get("/health")
def health():
    return {"status": "ok"}
