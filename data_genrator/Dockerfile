FROM python:3.10-slim

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY genrator.py .

CMD ["python", "genrator.py"]