
FROM python:latest
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN "pip install --no-cache-dir -r requirements.txt"
COPY Docker /code

WORKDIR /code
CMD "python /api_run.py"