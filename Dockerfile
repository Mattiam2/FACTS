FROM python:3.13-slim AS builder
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./ebsi_sim /code/ebsi_sim
CMD ["fastapi", "run", "ebsi_sim/main.py", "--port", "8000"]