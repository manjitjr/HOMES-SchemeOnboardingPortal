from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Settings(BaseSettings):
    # Switch to your Neon URL when ready:
    # database_url: str = "postgresql+asyncpg://user:pass@your-neon-host.neon.tech/dbname?sslmode=require"
    database_url: str = "sqlite+aiosqlite:///./homes_onboarding.db"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
