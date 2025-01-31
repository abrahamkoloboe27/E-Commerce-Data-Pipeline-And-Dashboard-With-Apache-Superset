FROM apache/airflow:slim-latest-python3.10

COPY requirements.txt .
COPY airflow.cfg /opt/airflow/airflow.cfg
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
