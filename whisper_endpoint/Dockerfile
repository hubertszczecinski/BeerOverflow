FROM pytorch/pytorch:2.9.1-cuda13.0-cudnn9-devel
LABEL authors="atopo"

COPY requirements.txt requirements.txt
COPY whisper-endpoint.py whisper-endpoint.py
COPY id_matching.py id_matching.py
COPY id.csv id.csv
RUN pip install --no-cache-dir  -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["serve", "run", "whisper-endpoint:depl"]