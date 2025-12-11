from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from decouple import config


# for-db(except sqlite)
# DB_HOST = config("DB_HOST")
# DB_NAME = config("DB_NAME")
# DB_USER = config("DB_USER")
# DB_PASS = config("DB_PASS")
# DB_PORT = config("DB_PORT")

# Path-to-sqlite.db
BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = BASE_DIR / "../app.db"

# 1. ASYNC CONNECTION (For FastAPI)
# DATABASE_URL_ASYNC = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_ASYNC = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"

engine = create_async_engine(DATABASE_URL_ASYNC, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session


# 2. SYNCHRONOUS CONNECTION (For Celery) <--- ADD THIS
# DATABASE_URL_SYNC = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# sync_engine = create_engine(DATABASE_URL_SYNC, echo=False, pool_pre_ping=True)
# SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


DATABASE_URL_SYNC = f"sqlite:///{SQLITE_DB_PATH}"
sync_engine = create_engine(
    DATABASE_URL_SYNC,
    echo=False,
    connect_args={"check_same_thread": False},  # required for SQLite multi-thread usage
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()
