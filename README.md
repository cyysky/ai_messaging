# AI Messaging Application

## Git Setup

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/cyysky/ai_messaging.git
git push -u origin main
```

## Application Setup

uv venv --python 3.13 .venv
source .venv/bin/activate

1. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies and run:

## Backend

```bash
python -m backend.main
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_MESSAGE_HOST` | Backend host | `0.0.0.0` |
| `AI_MESSAGE_PORT` | Backend port | `8000` |
| `AI_MESSAGE_DOMAIN` | API domain | `api.example.com` |
| `AI_MESSAGE_FRONTEND_PORT` | Frontend dev server port | `3000` |
| `AI_MESSAGE_FRONTEND_SSL` | Enable HTTPS for frontend dev server | `false` |
| `AI_MESSAGE_DATABASE_URL` | Database connection string | `sqlite:///./backend/backend.db` |
| `AI_MESSAGE_SSL_CERT` | SSL certificate path | `ssl/cert.pem` |
| `AI_MESSAGE_SSL_KEY` | SSL private key path | `ssl/key.pem` |

## SSL Setup

To enable HTTPS for the frontend dev server:
1. Set `AI_MESSAGE_FRONTEND_SSL=true` in `.env`
2. Ensure SSL certificates exist at the paths specified in `AI_MESSAGE_SSL_CERT` and `AI_MESSAGE_SSL_KEY`