FROM python:3.11-slim

WORKDIR /app

# OS deps for audio / stable-ts etc. Adjust as needed.
RUN apt-get update && apt-get install -y \
  ffmpeg \
  libsndfile1 \
&& rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy code and data
COPY src ./src
COPY data ./data

RUN #sed -i 's/\r$//' start.sh
RUN #chmod +x start.sh

EXPOSE 9000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9000"]