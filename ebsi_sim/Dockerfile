FROM python:3.13-slim AS builder
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]