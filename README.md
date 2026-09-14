# Site Monitor

Site Monitor is a lightweight tool that checks website availability based on a `config.json` file, logs the results into a `.csv` file, and sends real-time alerts via Discord webhook upon state changes.


## Features
- **Continuous Health Checks:** Checks website availability and response latency.
- **Metric Logging:** Saves check history (timestamp, URL, status code, response time) to a .csv file.
- **Discord Alerts:** Sends notifications on state changes (DOWN / RECOVERED) via webhook.
- **Containerized:** Ready to run with Docker and Docker Compose.

## Configuration 
Copy the template files and fill in your Discord webhook URL:
```
cp .env.example .env
cp config.example.json config.json
```

## Quick Start
```
docker compose up -d
docker compose logs -f
```