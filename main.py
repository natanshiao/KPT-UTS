from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import init_db
from routes import resource, transaction


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inisialisasi database sekali ketika aplikasi dimulai.
    await init_db()
    yield


app = FastAPI(
    # Malas...
    title="API Perpustakaan",
    description="REST API asynchronous dengan FastAPI dan aiosqlite",
    version="1.0.0",
    lifespan=lifespan,
)

# Router dipisah karena bapak yang minta.
app.include_router(resource.router, prefix="/resource", tags=["Resource"])
app.include_router(transaction.router,
                   prefix="/transaction", tags=["Transaction"])


@app.get("/")
async def root():
    return {"message": "API Perpustakaan berjalan"}
