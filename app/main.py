import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, cart, orders, payments

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Commerce Service is running"}

