# FACTS: Facts Authenticity and Credibility Tracking System

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
The EBSI Blockchain is simulated using FastAPI and a PostgreSQL database, including all the CRUD actions.

EBSI FactChecker is composed of 4 FastAPI applications:

- **EBSI-Sim**: this application simulates the EBSI Blockchain, in particular Authorisation API and Track'n'Trace API.
- **FACTS-Publish**: this application allows publishers (i.e. news agencies) to register their digital content (e.g.
  articles, videos, social posts) on the EBSI Blockchain.
- **FACTS-Check**: this application allows independent FactCheckers to register their assessments about the authenticity and the credibility of the
  digital content published on the EBSI Blockchain.
- **FACTS-Verify**: this application allows to check all the assessments made by independent FactCheckers about a digital content given a media url. It is also a browser extension.