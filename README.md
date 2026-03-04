# SSC Exam Prep Platform

AI-powered SSC (Staff Selection Commission) exam preparation platform with adaptive learning, daily question mining, and comprehensive analytics.

## Live Demo

- **Frontend**: https://personal-trainer-app-2yojwkh4.devinapps.com
- **Backend API**: https://personal-trainer-backend-ugzadqmc.fly.dev
- **API Docs (Swagger)**: https://personal-trainer-backend-ugzadqmc.fly.dev/docs

## Features

- **Dashboard** - Overview of all 6 SSC subjects (English, Indian Polity, Geography, Economics, History, Static GK) with topic and question counts
- **Quick Quiz** - Random questions from all subjects with instant feedback and explanations
- **Smart Quiz (Adaptive)** - AI-powered quiz that focuses on your weak areas based on past performance
- **Analytics** - Track your accuracy, time per question, and weak topics across all subjects
- **Admin Panel** - Trigger AI-powered question mining for individual subjects or all at once
- **Daily Mining** - Background scheduler automatically mines new questions every day using LLM + web search

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Recharts** for analytics charts
- **Lucide React** for icons

### Backend
- **FastAPI** (Python 3.12+)
- **SQLAlchemy 2.0** with async support (aiosqlite)
- **SQLite** for database (persistent volume on Fly.io)
- **APScheduler** for background mining jobs
- **Pydantic** for data validation

### AI/ML Services
- **LLM Router** with fallback chain: Groq -> Gemini -> Mistral
- **Search Router** with fallback chain: Tavily -> Serper -> DuckDuckGo
- Automatic daily rate limit tracking and API rotation

## Project Structure

```
Personal-Trainer/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Environment settings & API key config
│   │   │   └── database.py        # Async SQLAlchemy engine & session
│   │   ├── models/
│   │   │   ├── database.py        # SQLAlchemy ORM models
│   │   │   └── schemas.py         # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── analytics.py       # GET /analytics/{user_id}
│   │   │   ├── attempts.py        # POST /attempts
│   │   │   ├── mining.py          # POST /mining/trigger, /mining/trigger-all
│   │   │   ├── questions.py       # GET /questions, /questions/random, /questions/count
│   │   │   ├── quiz.py            # POST /quiz/adaptive
│   │   │   └── subjects.py        # GET /subjects, /subjects/{id}/topics
│   │   ├── services/
│   │   │   ├── adaptive_engine.py # Adaptive quiz generation & analytics
│   │   │   ├── background_jobs.py # APScheduler daily mining jobs
│   │   │   ├── llm_router.py      # Multi-provider LLM with fallback
│   │   │   ├── mining_engine.py   # Question mining pipeline
│   │   │   ├── search_router.py   # Multi-provider web search
│   │   │   └── seed_data.py       # Initial database seeding
│   │   └── main.py                # FastAPI app entry point
│   ├── pyproject.toml             # Python dependencies (Poetry)
│   └── .env                       # Environment variables (not committed)
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts             # API client functions
│   │   │   └── utils.ts           # Utility helpers
│   │   ├── pages/
│   │   │   ├── Admin.tsx          # Admin panel with mining controls
│   │   │   ├── Analytics.tsx      # User analytics dashboard
│   │   │   ├── Dashboard.tsx      # Main dashboard with subjects
│   │   │   └── Quiz.tsx           # Quiz interface (quick + adaptive)
│   │   ├── types/
│   │   │   └── api.ts             # TypeScript type definitions
│   │   ├── App.tsx                # Root component with routing
│   │   └── main.tsx               # Entry point
│   ├── package.json               # Node dependencies
│   └── .env                       # Frontend environment variables
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check |
| GET | `/subjects` | List all subjects with topic/question counts |
| GET | `/subjects/{id}/topics` | List topics for a subject |
| GET | `/questions` | List questions (filterable by subject, topic, difficulty) |
| GET | `/questions/random` | Get random questions for quiz |
| GET | `/questions/count` | Get total question count |
| GET | `/questions/{id}` | Get a specific question with answer |
| POST | `/questions/generate` | Generate new questions via AI |
| POST | `/attempts` | Record a user's quiz attempt |
| GET | `/analytics/{user_id}` | Get user analytics (accuracy, time, etc.) |
| GET | `/analytics/{user_id}/weak-topics` | Get user's weak topics |
| POST | `/quiz/adaptive` | Generate adaptive quiz based on weak areas |
| POST | `/mining/trigger` | Trigger mining for one subject |
| POST | `/mining/trigger-all` | Trigger mining for all subjects |
| GET | `/mining/logs` | View mining history |
| GET | `/mining/api-usage` | View API usage stats |

---

## Deployment Guide

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm
- **Poetry** (Python package manager): `pip install poetry`
- API keys for at least one LLM provider and one search provider (see [Environment Variables](#environment-variables))

### Environment Variables

#### Backend (`backend/.env`)

```env
# Database (SQLite - no external DB required)
DATABASE_URL=sqlite+aiosqlite:///./ssc_exam.db

# LLM API Keys (at least one required for question mining)
GROQ_API_KEY=your_groq_api_key          # Get from https://console.groq.com
GEMINI_API_KEY=your_gemini_api_key      # Get from https://aistudio.google.com/apikey
MISTRAL_API_KEY=your_mistral_api_key    # Get from https://console.mistral.ai

# Search API Keys (at least one required for mining with web search)
TAVILY_API_KEY=your_tavily_api_key      # Get from https://tavily.com
SERPER_API_KEY=your_serper_api_key      # Get from https://serper.dev
```

#### Frontend (`frontend/.env`)

```env
# Backend API URL (change this to your deployed backend URL)
VITE_API_URL=http://localhost:8000
```

---

### Option 1: Local Development

#### 1. Clone the repository

```bash
git clone https://github.com/nitish081999/Personal-Trainer.git
cd Personal-Trainer
git checkout devin/1772635241-ssc-exam-platform
```

#### 2. Set up the backend

```bash
cd backend

# Install dependencies
poetry install

# Create .env file with your API keys
cp .env.example .env   # Or create manually (see Environment Variables above)

# Run the backend server
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will:
- Create the SQLite database automatically
- Seed it with 6 subjects, 70+ topics, and 19 sample questions
- Start the background mining scheduler
- Serve the API at http://localhost:8000
- Swagger docs available at http://localhost:8000/docs

#### 3. Set up the frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run the dev server
npm run dev
```

The frontend will be available at http://localhost:5173

---

### Option 2: Deploy to a VPS (Ubuntu/Debian)

#### 1. Server setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+, Node.js 18+, and nginx
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# Install Poetry
pip install poetry
```

#### 2. Deploy the backend

```bash
# Clone and enter project
git clone https://github.com/nitish081999/Personal-Trainer.git
cd Personal-Trainer
git checkout devin/1772635241-ssc-exam-platform

cd backend

# Install dependencies
poetry install --no-dev

# Create .env with your API keys
cat > .env << 'EOF'
DATABASE_URL=sqlite+aiosqlite:///./ssc_exam.db
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
EOF

# Test that it starts
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Press Ctrl+C after confirming it works
```

#### 3. Create a systemd service for the backend

```bash
sudo tee /etc/systemd/system/ssc-backend.service << 'EOF'
[Unit]
Description=SSC Exam Prep Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Personal-Trainer/backend
Environment="PATH=/path/to/Personal-Trainer/backend/.venv/bin"
ExecStart=/path/to/Personal-Trainer/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ssc-backend
sudo systemctl start ssc-backend

# Check status
sudo systemctl status ssc-backend
```

#### 4. Build and deploy the frontend

```bash
cd /path/to/Personal-Trainer/frontend

# Set the backend URL to your server's domain/IP
echo "VITE_API_URL=https://yourdomain.com/api" > .env

# Build the production bundle
npm install
npm run build

# Copy the build output to nginx
sudo cp -r dist/* /var/www/html/ssc-exam/
```

#### 5. Configure Nginx

```bash
sudo tee /etc/nginx/sites-available/ssc-exam << 'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (static files)
    root /var/www/html/ssc-exam;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/ssc-exam /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. (Optional) Add SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

### Option 3: Deploy to Fly.io

#### 1. Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

#### 2. Deploy the backend

```bash
cd backend

# Create a Fly app
fly launch --name ssc-exam-backend --region sjc --no-deploy

# Create a persistent volume for SQLite
fly volumes create data --size 1 --region sjc

# Set environment secrets
fly secrets set GROQ_API_KEY=your_key_here
fly secrets set GEMINI_API_KEY=your_key_here
fly secrets set MISTRAL_API_KEY=your_key_here
fly secrets set TAVILY_API_KEY=your_key_here

# Create fly.toml (if not auto-generated)
cat > fly.toml << 'EOF'
app = "ssc-exam-backend"
primary_region = "sjc"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  DATABASE_URL = "sqlite+aiosqlite:////data/app.db"

[mounts]
  source = "data"
  destination = "/data"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
EOF

# Deploy
fly deploy
```

#### 3. Build and deploy the frontend

```bash
cd frontend

# Set backend URL
echo "VITE_API_URL=https://ssc-exam-backend.fly.dev" > .env

# Build
npm install && npm run build

# Deploy to any static hosting (Vercel, Netlify, Fly.io, etc.)
# Example with Vercel:
npx vercel --prod dist/

# Or with Netlify:
npx netlify deploy --prod --dir=dist
```

---

### Option 4: Deploy with Docker

#### 1. Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /data

ENV DATABASE_URL=sqlite+aiosqlite:////data/app.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### 3. Docker Compose

Create `docker-compose.yml` in the project root:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - db-data:/data
    env_file:
      - ./backend/.env
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: http://localhost:8000
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  db-data:
```

#### 4. Run with Docker Compose

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

---

## Mining Questions with AI

The platform can automatically mine new SSC exam questions using AI. There are two ways:

### Manual Mining (Admin Panel)
1. Go to the **Admin** page
2. Click **"Mine All Subjects"** to mine questions for all 6 subjects
3. Or use the API: `POST /mining/trigger` with `{"subject_id": 1, "count": 20}`

### Automatic Daily Mining
The backend runs a background scheduler that automatically mines questions daily for each subject. This is configured in `backend/app/services/background_jobs.py`.

### How Mining Works
1. **Search Query Generation**: LLM generates targeted search queries for a subject/topic
2. **Web Search**: Searches the web using Tavily/Serper/DuckDuckGo for educational content
3. **MCQ Extraction**: LLM extracts structured MCQs from the web content
4. **Synthetic Fallback**: If web search fails, LLM generates questions directly
5. **Deduplication**: SHA-256 hash prevents duplicate questions
6. **Database Insert**: Valid questions are stored with metadata

---

## Troubleshooting

### Backend won't start
- Ensure Python 3.12+ is installed: `python3 --version`
- Ensure Poetry is installed: `poetry --version`
- Run `poetry install` to install dependencies
- Check `.env` file exists with required variables

### Frontend shows "No subjects" or empty dashboard
- Verify the backend is running and accessible
- Check `VITE_API_URL` in `frontend/.env` points to the correct backend URL
- Check browser console for CORS or network errors
- Verify backend health: `curl http://localhost:8000/healthz`

### Mining not working
- Ensure at least one LLM API key is set (GROQ_API_KEY, GEMINI_API_KEY, or MISTRAL_API_KEY)
- Check backend logs for API errors
- Verify API key quotas haven't been exceeded

### Database issues
- Delete the SQLite file and restart to reseed: `rm backend/ssc_exam.db`
- The app will recreate the database and seed it on next startup

## License

MIT
