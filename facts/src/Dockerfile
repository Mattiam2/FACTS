FROM python:3.13-slim AS builder
WORKDIR /code
COPY ./ /code/src
RUN pip install --no-cache-dir --upgrade -r /code/src/requirements.txt
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]