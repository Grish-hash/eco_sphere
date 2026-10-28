from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, warehouses, routes, risk

Base.metadata.create_all(bind=engine)  # creates tables on first run

app = FastAPI(title="EcoSphere API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(warehouses.router)
app.include_router(routes.router)
app.include_router(routes.fleet_router)
app.include_router(risk.router)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
