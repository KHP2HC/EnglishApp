# EnglishCoach Pro Web Migration

This repository now includes a web backend and frontend scaffold for the vocabulary and reading stages.

## Backend

The backend is implemented with FastAPI in `web/api.py`.

### Install dependencies
```bash
cd d:\EnglishCoachPro
pip install -r requirements.txt
```

### Run locally
```bash
uvicorn web.api:app --reload
```

The backend will be available at `http://localhost:8000`.

## Frontend

The frontend is a React + Vite app in `web/frontend`.

### Install dependencies
```bash
cd d:\EnglishCoachPro\web\frontend
npm install
```

### Run locally
```bash
npm run dev
```

Open the browser at the local URL shown by Vite.

## Docker

A backend Dockerfile, frontend Dockerfile, and `docker-compose.yml` are included.

### Run with Docker Compose
```bash
cd d:\EnglishCoachPro
docker compose up --build
```

Then access:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:4173`

## Notes

- The frontend currently uses a placeholder `user_id=1` for API calls.
- The reading endpoint returns a random test by default.
- Adjust `VITE_API_BASE` in `web/frontend/Dockerfile` or local env to point to your backend URL.
