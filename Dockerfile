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
COPY ./facts/src /code/facts/src
COPY ./facts/__init__.py /code/facts/
CMD ["fastapi", "run", "facts/src/main.py", "--port", "8000"]

FROM node:lts-alpine AS facts_frontend_builder
RUN npm install -g http-server
WORKDIR /app
COPY ./facts/frontend .
RUN npm install
RUN npm run build
CMD http-server dist -a $FACTS_FRONTEND_HOST -p $FACTS_FRONTEND_PORT -P http://$FACTS_FRONTEND_HOST:$FACTS_FRONTEND_PORT?