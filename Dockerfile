FROM apache/airflow:3.1.0

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

USER root

RUN apt update
RUN python3 -m pip install playwright
RUN python3 -m playwright install --with-deps

USER airflow

RUN playwright install
