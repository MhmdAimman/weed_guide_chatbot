# Weed Guide Chatbot

A full-stack chatbot for the Las Animas County Weed Management Pocket Guide. The app uses a FastAPI backend, a React/Vite frontend, OpenAI, and ChromaDB to answer weed identification and control questions using the local guide PDF.

## Live Services

Frontend:

```text
https://weed-guide-chatbot-36e24akv5-mohammed-aimman-s-projects.vercel.app/
Backend:
https://weed-guide-chatbot.onrender.com
Health check:
https://weed-guide-chatbot.onrender.com/api/health
Tech Stack
- FastAPI
- Uvicorn
- OpenAI API
- ChromaDB
- PyPDF
- React
- Vite
- Tailwind CSS
- Render
- Vercel
Project Structure
weed-guide/
  backend/
    main.py
    chatbot.py
    config.py
    vector_store.py
    ingest.py
    manual.pdf
    pyproject.toml
    uv.lock
  frontend/
    src/
    package.json
    vite.config.js
Backend Setup
From the backend directory:
uv sync
Create a .env file:
OPENAI_API_KEY=your_openai_api_key
FRONTEND_ORIGIN=http://localhost:5173
Ingest the PDF into ChromaDB:
uv run python ingest.py
Run the backend:
uv run uvicorn main:app --host 0.0.0.0 --port 8000
Backend runs at:
http://localhost:8000
Frontend Setup
From the frontend directory:
npm install
Create a .env file if needed:
VITE_API_BASE_URL=http://localhost:8000
Run the frontend:
npm run dev
Frontend runs at:
http://localhost:5173
API Endpoints
Health check:
GET /api/health
Chat endpoint:
POST /api/chat
Example body:
{
  "message": "How do I identify Canada thistle?",
  "state": null
}
Render Deployment
Use these backend settings on Render:
Root Directory: backend
Build Command: uv sync && uv run python ingest.py
Start Command: uv run uvicorn main:app --host 0.0.0.0 --port $PORT
Required Render environment variables:
OPENAI_API_KEY=your_openai_api_key
FRONTEND_ORIGIN=https://weed-guide-chatbot.vercel.app
Vercel Deployment
Use these frontend settings on Vercel:
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Required Vercel environment variable:
VITE_API_BASE_URL=https://weed-guide-chatbot.onrender.com
After changing environment variables, redeploy the service.
