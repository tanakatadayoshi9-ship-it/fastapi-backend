# FastAPI CRUD Project

## Tech Stack
- Python 3.12
- FastAPI
- SQLite (aiosqlite)
- Uvicorn

## Features
- Create item
- Read items
- Read item by id
- Update item
- Delete item

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
