# import asyncio
# from database import engine, Base

# print("ENGINE", engine)
# async def create():
#     async with engine.begin() as conn:
#         try:
#             print("CONN", conn)
#             await conn.run_sync(Base.metadata.create_all)
#             print("✅ Tables created successfully")
#         except Exception as e:
#             print("Not creataed table")
#             print("ERROR", str(e))

# asyncio.run(create())

import pymysql
from decouple import config

DB_HOST = config("DB_HOST")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_PORT = int(config("DB_PORT"))

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT,
    charset="utf8mb4",
    autocommit=True
)

try:
    with connection.cursor() as cursor:
        # Create Database (if not exists)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # Create UploadCSV => upload_jobs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS upload_jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_path VARCHAR(100) NOT NULL,
            original_filename VARCHAR(100) NOT NULL,
            status ENUM('PENDING','PROCESSING','SUCCESS','FAILED') NOT NULL DEFAULT 'PENDING',
            error_message TEXT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """)

        # Create CSVData => csv_data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS csv_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id INT,
            name VARCHAR(100),
            role VARCHAR(100),
            loc VARCHAR(100),
            extra VARCHAR(100),
            FOREIGN KEY (job_id) REFERENCES upload_jobs(id) ON DELETE CASCADE
        );
        """)

        print("\n🎉 Tables created successfully in database:", DB_NAME)

except Exception as e:
    print("❌ Error:", e)

finally:
    connection.close()
