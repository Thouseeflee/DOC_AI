FROM python:3.11-slim

WORKDIR /app

# Install minimal system requirements to ensure wheels work or build succeeds
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the application
CMD streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
