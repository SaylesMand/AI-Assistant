FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src ./src
COPY .env .env
COPY ./data ./data

CMD ["uvicorn", "src.main:app", "--port", "8000", "--host", "0.0.0.0"]