# 1️⃣ Use base python image
FROM python:3.12-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy only requirements first
COPY requirements.txt .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy everything including .env file
COPY . .

# 6️⃣ Expose FastAPI port
EXPOSE 8000

# 7️⃣ Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
