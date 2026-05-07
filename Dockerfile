FROM python:3.13-slim AS ebsi_sim_builder
WORKDIR /code
COPY ebsi_sim/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./ebsi_sim /code/ebsi_sim
CMD ["fastapi", "run", "ebsi_sim/src/main.py", "--port", "8000"]

FROM python:3.13-slim AS facts_backend_builder
WORKDIR /code
COPY facts/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./facts /code/facts
CMD ["fastapi", "run", "facts/src/main.py", "--port", "8000"]