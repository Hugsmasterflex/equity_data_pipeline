FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only package/module files; bind mount will override in dev
COPY . .

# Default command (overridden by compose)
CMD ["python", "-m", "ingestion.run_once"]
