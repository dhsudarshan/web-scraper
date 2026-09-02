# Price Tracker
A containerized Python price tracker that automates web scraping using Playwright and safely logs historical pricing from Daraz website into a persistent PostgreSQL database.  
## Tech Stack
- Core: Python 3.11 running in a slim Debian container equipped with Google Chrome.  
- Scraper: Playwright for handling dynamic web elements and rendering.  
- Database: PostgreSQL 15 running inside an isolated Docker network with persistent volume storage. 
- Orchestration: Docker Compose to spin up the entire pipeline with a single command.  
## Project Structure
scraper.py — Handles browser automation, data parsing, and database injection.  
db.py — Manages database connection pooling, schema initialization, and upsert logic.  
Dockerfile — Configures the Python environment and installs Chrome dependencies.  
docker-compose.yaml — Orchestrates the database container and the scraper runner service.  
## Quick Start
Ensure Docker and Docker Compose are installed on your machine.Build and launch the containerized environment in the background:  
Bash
```
docker compose up --build -d
```
The scraper will automatically initialize the database schema and store the latest product pricing points.  
## Database Architecture
- Products Table: Utilizes an internal auto-incrementing integer surrogate key (id) alongside the external provider's unique string identifier (item_id).  
- Price History Table: Relates back to products via a stable foreign key constraint (product_id) with cascade deletes, preventing data corruption if external keys shift.  
