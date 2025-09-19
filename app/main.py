import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, cart
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Commerce Service is starting up...")
    yield
    logger.info("Commerce Service is shutting down...")


app = FastAPI(
    title="Commerce Service",
    description="A modern, high-performance API for e-commerce operations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
       allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)

app.include_router(products.router)
app.include_router(cart.router)



@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Commerce Service is running"}

