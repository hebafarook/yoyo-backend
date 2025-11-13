# YoYo Elite Soccer AI – Backend

FastAPI backend for the YoYo Elite Soccer AI app.

## Endpoints

- `GET /health` – health check
- `POST /api/programs/generate` – generate a 4-week training program.

**Body / params:**

- `player_id` (query or body) – ID of the player in the database.

## Env variables (not committed to GitHub)

- `MONGO_URL`
- `DB_NAME` (default: `yoyo_db`)
- `OPENAI_API_KEY`
- `CORS_ORIGINS` (default: `*`)
