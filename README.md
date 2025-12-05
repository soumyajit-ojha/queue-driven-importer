# 🚀 Async CSV Importer (FastAPI + Celery + MySQL)

A high-performance, queue-driven application designed to handle large CSV uploads asynchronously. It utilizes **FastAPI** for non-blocking I/O, **Celery** for background processing, **Redis** as a message broker, and **MySQL** for persistent storage.

## 🏗 Architecture

The system is designed to handle heavy loads without blocking the main API thread.

1.  **FastAPI:** Receives file, saves to disk, creates a DB Job entry, and pushes a task to Redis.
2.  **Redis:** Queues the task.
3.  **Celery Worker:** Picks up the task, processes the CSV, inserts rows into MySQL, and **deletes the file** upon success.
4.  **MySQL:** Stores Job status (`PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`) and parsed CSV data.

---

## 🛠️ Tech Stack

*   **Framework:** FastAPI (Python 3.10+)
*   **Database:** MySQL 8.0
*   **ORM:** SQLAlchemy (Async for API, Sync for Worker)
*   **Queue/Broker:** Redis
*   **Worker:** Celery
*   **Server:** Uvicorn / Gunicorn

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory.

```ini
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=csv_worker
DB_USER=root
DB_PASS=yourpassword

# Celery Configuration
# If using Docker, usually: redis://redis:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🐳 Deployment with Docker (Recommended)

For production or easy local setup, use **Docker Compose**.

### 1. Structure
Ensure your project directory looks like this:
```text
.
├── app/
│   ├── main.py              # FastAPI app, routes
│   ├── config.py            # Settings (DB URL, Redis URL, etc.)
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models.py            # DB models (UploadJob, ExtractedRow)
│   ├── schemas.py           # Pydantic schemas
│   ├── celery_app.py        # Celery instance setup
│   ├── tasks.py             # Celery tasks (CSV processing)
│   └── utils.py             # CSV helpers, common functions
├── worker.py                # Celery worker entry
├── requirements.txt
├── create_db.py
└── docker-compose.yml       # Redis + app (optional but useful)
```

### 2. Docker Compose
Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./uploads:/app/uploads
    env_file: .env
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  worker:
    build: .
    command: celery -A app.celery.celery worker --loglevel=info
    volumes:
      - ./uploads:/app/uploads
    env_file: .env
    depends_on:
      - db
      - redis

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: yourpassword
      MYSQL_DATABASE: csv_worker
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

### 3. Run
```bash
docker-compose up --build -d
```

### 4. Initialize Database
Once the containers are running, initialize the tables:
```bash
docker-compose exec api python app/create_tables.py
```

---

## 💻 Local Development (Manual)

If you are running without Docker:

### 1. Prerequisites
*   Python 3.10+
*   MySQL Server running
*   Redis Server running

### 2. Installation
```bash
# Create virtual env
python -m venv .venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize DB
Make sure your `.env` points to your local MySQL.
```bash
python create_db.py
```

### 4. Run API Server
```bash
uvicorn app.main:app --reload
```

### 5. Run Celery Worker
Open a new terminal:
```bash
celery -A app.celery.celery worker --loglevel=info --pool=solo # synchoronus
# or
celery -A app.celery worker --pool=threads --concurrency=4 --loglevel=info # asynchoronus

# Note: --pool=solo is recommended for Windows. On Linux/Mac use --pool=prefork or default.
```

---

## 📡 API Documentation

Once running, visit **Swagger UI** at: `http://localhost:8000/docs`

### 1. Upload CSV
*   **Endpoint:** `POST /upload`
*   **Body:** `multipart/form-data` (key: `file`)
*   **Response:**
    ```json
    {
      "job_id": 1,
      "status": "PENDING",
      "message": "Upload successful. Processing started in background."
    }
    ```

### 2. Check Status & Get Data
*   **Endpoint:** `GET /jobs/{job_id}`
*   **Response (While Processing):**
    ```json
    {
      "id": 1,
      "original_filename": "data.csv",
      "status": "PROCESSING",
      "csv_data": []
    }
    ```
*   **Response (Success):**
    ```json
    {
      "id": 1,
      "original_filename": "data.csv",
      "status": "SUCCESS",
      "csv_data": [
        { "name": "John", "role": "Dev", "loc": "NY", "extra": "..." }
      ]
    }
    ```

---

## ⚠️ Production Considerations

If deploying this to a live server (AWS/DigitalOcean/etc):

1.  **File Storage:**
    *   Currently, files are saved to the local filesystem (`./uploads`).
    *   In a clustered environment (Kubernetes/Multiple ECS nodes), you must use a **Shared Volume** (EFS/NFS) or modify `utils.py` to upload to **S3** instead of local disk.

2.  **Concurrency:**
    *   Celery workers handle tasks. To process more files simultaneously, increase the worker concurrency:
    *   `celery -A app.celery.celery worker --concurrency=10 ...`

3.  **Process Management:**
    *   Do not run `uvicorn` or `celery` directly in the shell. Use **Gunicorn** for the API and **Supervisor** or **Systemd** for the worker.

4.  **Database Connection Pooling:**
    *   The code uses SQLAlchemy with proper pooling (`pool_pre_ping=True`). ensure your MySQL `max_connections` setting is higher than `(API_Workers + Celery_Workers) * Pool_Size`.