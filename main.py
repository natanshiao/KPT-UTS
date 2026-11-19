from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import init_db
from routes import resource, transaction_lock as transaction


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inisialisasi database saat server dimulai.
    await init_db()
    yield


app = FastAPI(
    title="API Perpustakaan",
    description="REST API asynchronous dengan FastAPI dan aiosqlite",
    version="1.0.0",
    lifespan=lifespan,
)

# Router CRUD buku.
app.include_router(
    resource.router,
    prefix="/resource",
    tags=["Resource"]
)

# Router transaksi.
# Prefix /transaction sudah ditentukan di transaction.py.
app.include_router(transaction.router)


@app.get("/")
async def root():
    return {"message": "API Perpustakaan berjalan"}
