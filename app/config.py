from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Settings(BaseSettings):
    # Switch to your Neon URL when ready:
    # database_url: str = "postgresql+asyncpg://user:pass@your-neon-host.neon.tech/dbname?sslmode=require"
    database_url: str = "sqlite+aiosqlite:///./homes_onboarding.db"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_sender: str = "homes-onboarding@localhost"
    app_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
