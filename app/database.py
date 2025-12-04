from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine # <--- Import Sync Engine
from decouple import config

DB_HOST = config("DB_HOST")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_PORT = config("DB_PORT")

# 1. ASYNC CONNECTION (For FastAPI)
DATABASE_URL_ASYNC = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

# 2. SYNCHRONOUS CONNECTION (For Celery) <--- ADD THIS
DATABASE_URL_SYNC = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()
