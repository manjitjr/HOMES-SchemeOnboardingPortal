import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import engine, async_session
from app.models import Base
from app.auth import router as auth_router, seed_demo_users
from app.routers.schemes import router as schemes_router
from app.routers.scheduling import router as scheduling_router

STATIC_DIR = pathlib.Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add missing columns for migration
        def migrate_tables():
            import sqlite3
            try:
                db_path = "db.sqlite3"
                sqlite_conn = sqlite3.connect(db_path)
                cursor = sqlite_conn.cursor()
                try:
                    cursor.execute("ALTER TABLE scheme_overview ADD COLUMN is_active BOOLEAN DEFAULT 1")
                except sqlite3.OperationalError:
                    pass
                sqlite_conn.commit()
                sqlite_conn.close()
            except Exception as e:
                print(f"Migration note: {e}")
        
        await conn.run_sync(lambda _: migrate_tables())
    
    async with async_session() as db:
        await seed_demo_users(db)
    yield


app = FastAPI(
    title="HOMES Schemes Onboarding API",
    description="Scheme onboarding management for MOH HOMES",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(schemes_router)
app.include_router(scheduling_router)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
