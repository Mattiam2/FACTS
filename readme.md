# FACTS: Facts Authenticity and Credibility Tracking System

Author: Mattia Maglie (ID: 2095330)\
Supervisor: Prof. Mauro Migliardi\
University of Padova

This repository contains the source code of my thesis project for the Master Degree in Computer Engineering.

## Project description

This project is part of the Master Degree in Computer Engineering at the University of Padova.
Its goal is to develop a set of web applications which, using
the [EBSI Blockchain](https://ec.europa.eu/digital-building-blocks/sites/spaces/EBSI/pages/447687044/Home), will
allow to verify the source and the authenticity of any digital content (i.e. articles, videos, social posts) and check
the
credibility of the publisher and the content itself, thanks to the assessments made by independent FactCheckers.

The project is developed in Python using the [FastAPI](https://fastapi.tiangolo.com/) framework for the backend and
JavaScript using the [VueJS](https://vuejs.org/) for the frontend.
The EBSI Blockchain is simulated using FastAPI and a PostgreSQL database, including all the transactions operations.

EBSI FactChecker is composed of 4 FastAPI applications:

- **EBSI-Sim**: this application simulates the EBSI Blockchain, in particular Authorisation API and Track'n'Trace API.
- **FACTS-Backend**: this application exposes API that allows:
    - Publishers (i.e. news agencies) to register their digital content (e.g.
      articles, videos, social posts) on the EBSI Blockchain.
    - Fact-Checkers to register their assessments about the authenticity
      and the credibility of the digital content published (or not) on the EBSI Blockchain.
    - Users to check the authenticity and the credibility of the digital content published on the EBSI Blockchain.
- **FACTS-Frontend**: this application provides a web application that allows:
    - Publishers and Fact-Checkers to link their Wallet, onboard on EBSI, and publish article claims or assessments.
    - Users to view article claims and assessments scores, allowing them to search by URL
- **FACTS-Extension**: chrome extension that allows users while searching the web to check the authenticity and the
  assessments scores of a website.

## How to run EBSI Simulator & FACTS

1. Clone the repository
2. Install Docker Engine and Docker Compose
3. Run the command `docker-compose up` from the root directory
4. Five containers will be started:
   - `ebsi_sim`: Container running the EBSI Simulator APIs - Exposed on port 8000
   - `ebsi_db`: PostgreSQL database which EBSI Simulator will use
   - `facts_backend`: Container running the FACTS Backend API - Exposed on port 8001
   - `facts_frontend`: Container running the FACTS Frontend Web application - Exposed on port 8080
   - `facts_db`: PostgreSQL database which FACTS Backend will use as a simulated blockchain indexer
5. Open the browser and go to `http://localhost:8080` for the FACTS Frontend Web application 
6. Go to `http://localhost:8000/docs` for the Swagger API documentation of the EBSI Simulator
7. Go to `http://localhost:8001/docs` for the Swagger API documentation of the FACTS Backend

## How to run FACTS Extension

1. Clone the repository
2. Open the browser and go to `chrome://extensions/`
3. Enable Developer Mode
4. Click on `Load unpacked extension...` and select the `facts_extension` folder inside the repository
5. Enjoy