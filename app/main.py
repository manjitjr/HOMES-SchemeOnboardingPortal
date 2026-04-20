import pathlib
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import engine, async_session
from app.models import Base, sg_now
from app.auth import router as auth_router, seed_demo_users
from app.routers.schemes import router as schemes_router
from app.routers.scheduling import router as scheduling_router
from app.routers.guidance import router as guidance_router

STATIC_DIR = pathlib.Path(__file__).parent / "static"
LEGACY_TIMESTAMP_MIGRATION_KEY = "legacy_timestamps_shifted_to_sg_v1"


def _shift_legacy_timestamp(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None

    raw = str(raw_value).strip()
    if not raw:
        return None

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is not None:
        return raw

    shifted = parsed + timedelta(hours=8)
    separator = "T" if "T" in raw else " "
    return shifted.isoformat(sep=separator)


def _backfill_legacy_timestamps(cursor) -> int:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS app_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cursor.execute("SELECT value FROM app_meta WHERE key = ?", (LEGACY_TIMESTAMP_MIGRATION_KEY,))
    existing = cursor.fetchone()
    if existing and existing[0] == "done":
        return 0

    targets = [
        ("scheme_master", "id", ["created_at"]),
        ("scheme_submissions", "id", ["created_at", "updated_at"]),
        ("change_log", "id", ["timestamp"]),
        ("comments", "id", ["created_at"]),
        ("onboarding_slots", "id", ["booked_at", "updated_at"]),
        ("field_guidance", "id", ["created_at", "updated_at"]),
        ("users", "id", ["last_login_at", "last_logout_at"]),
    ]

    updates = 0
    for table_name, id_column, timestamp_columns in targets:
        for column_name in timestamp_columns:
            cursor.execute(
                f"SELECT {id_column}, {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL"
            )
            for row_id, raw_value in cursor.fetchall():
                shifted_value = _shift_legacy_timestamp(raw_value)
                if shifted_value is None or shifted_value == raw_value:
                    continue
                cursor.execute(
                    f"UPDATE {table_name} SET {column_name} = ? WHERE {id_column} = ?",
                    (shifted_value, row_id),
                )
                updates += 1

    cursor.execute(
        "INSERT OR REPLACE INTO app_meta (key, value) VALUES (?, ?)",
        (LEGACY_TIMESTAMP_MIGRATION_KEY, "done"),
    )
    return updates


def run_sqlite_migrations(db_path: str = "homes_onboarding.db") -> int:
    import sqlite3

    sqlite_conn = sqlite3.connect(db_path)
    try:
        cursor = sqlite_conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scheme_master (
                id TEXT PRIMARY KEY,
                agency TEXT NOT NULL,
                scheme_name TEXT NOT NULL,
                scheme_code TEXT,
                created_by TEXT,
                created_at DATETIME
            )
            """
        )
        try:
            cursor.execute("ALTER TABLE scheme_overview ADD COLUMN is_active BOOLEAN DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE scheme_submissions ADD COLUMN scheme_master_id TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE scheme_submissions ADD COLUMN valid_from DATE")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE scheme_submissions ADD COLUMN valid_to DATE")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE scheme_submissions ADD COLUMN cloned_from_submission_id TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_logout_at DATETIME")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS field_guidance (
                id TEXT PRIMARY KEY,
                tab_name TEXT NOT NULL,
                field_name TEXT NOT NULL,
                inline_hint TEXT,
                popover_title TEXT,
                popover_description TEXT,
                popover_examples TEXT,
                popover_do TEXT,
                popover_dont TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                UNIQUE(tab_name, field_name)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_log (
                id TEXT PRIMARY KEY,
                submission_id TEXT,
                stage TEXT,
                subject TEXT NOT NULL,
                recipients TEXT,
                delivery_status TEXT NOT NULL,
                detail TEXT,
                triggered_by TEXT,
                created_at DATETIME
            )
            """
        )

        import uuid

        default_fields = [
            ("overview", "agency"),
            ("overview", "scheme_name"),
            ("overview", "scheme_code"),
            ("overview", "valid_from"),
            ("overview", "valid_to"),
            ("overview", "legislated_or_consent"),
            ("overview", "consent_scope"),
            ("overview", "background_info"),
            ("mt_parameters", "mt_threshold"),
            ("mt_parameters", "mt_band"),
            ("transactions", "transaction_type"),
            ("transactions", "amount"),
            ("homes_functions", "function_name"),
            ("homes_functions", "enabled"),
            ("mt_bands", "band_name"),
            ("mt_bands", "band_value"),
            ("api_interfaces", "interface_name"),
            ("api_interfaces", "endpoint"),
        ]

        for tab_name, field_name in default_fields:
            cursor.execute(
                """
                INSERT OR IGNORE INTO field_guidance
                (id, tab_name, field_name, inline_hint, popover_title, popover_description,
                 popover_examples, popover_do, popover_dont, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()), tab_name, field_name,
                    "", "", "",
                    "[]", "[]", "[]",
                    sg_now().isoformat(), sg_now().isoformat()
                ),
            )

        updated_count = _backfill_legacy_timestamps(cursor)
        sqlite_conn.commit()
        return updated_count
    finally:
        sqlite_conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        def migrate_tables():
            try:
                updated_count = run_sqlite_migrations()
                if updated_count:
                    print(f"Migration note: shifted {updated_count} legacy timestamps to UTC+08")
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
app.include_router(guidance_router)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
