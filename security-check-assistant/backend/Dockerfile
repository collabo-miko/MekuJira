FROM python:3.11-slim

# Install git for PageIndex
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone PageIndex repository
RUN git clone --depth 1 https://github.com/VectifyAI/PageIndex.git /app/pageindex

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PageIndex dependencies
RUN pip install --no-cache-dir -r /app/pageindex/requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
