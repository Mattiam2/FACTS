FROM python:3.13 AS builder
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ebsi_sim /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]