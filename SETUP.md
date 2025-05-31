# PODVOX Setup Guide

## 🚀 Complete Setup (Frontend + Backend)

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ContextualisedVoicenotes
```

### 2. Install All Dependencies
```bash
# Install both backend and frontend dependencies
npm run install-all
```

### 3. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your API keys:
# - SIEVE_API_KEY (required)
# - ELEVENLABS_API_KEY (optional for now)
```

### 4. Run the Complete Application
```bash
# Start both frontend and backend simultaneously
npm run dev
```

This will start:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173

---

## 🔧 Individual Setup

### Backend Only
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing the Application

1. **Open the frontend** at http://localhost:5173
2. **Enter a podcast URL** (YouTube, Spotify, etc.)
3. **Add recipient details**
4. **Click "Generate Personalized Voicenote"**
5. **Watch the processing progress**
6. **Download your generated MP4**

---

## 📊 Architecture

```
PODVOX/
├── app/                    # FastAPI Backend
│   ├── main.py            # Main API endpoints
│   ├── services/          # Business logic
│   └── models/            # Data models
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/    # UI Components
│   │   └── App.tsx        # Main App
│   └── dist/              # Built assets
└── docs/                  # Documentation
```

---

## 🔗 API Integration

The frontend communicates with the backend via these endpoints:

### Generate Voicenote
```http
POST /generate
Content-Type: application/json

{
  "podcast_url": "https://www.youtube.com/watch?v=...",
  "recipient_name": "John Doe",
  "podcast_name": "The Example Show"
}
```

### Health Check
```http
GET /healthcheck
```

---

## 🚨 Troubleshooting

### Frontend Issues
- **Port 5173 in use**: Change port in `frontend/vite.config.ts`
- **API connection failed**: Ensure backend is running on port 8000
- **Build errors**: Clear node_modules and reinstall

### Backend Issues  
- **Port 8000 in use**: Change port in startup command
- **Missing API keys**: Check .env file configuration
- **Import errors**: Ensure virtual environment is activated

### CORS Issues
If frontend can't connect to backend:
```python
# In app/main.py, ensure CORS is configured:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📱 Development Workflow

1. **Make changes** to frontend/backend
2. **Both servers auto-reload** during development
3. **Test in browser** at http://localhost:5173
4. **API logs** visible in terminal
5. **Build for production** with `npm run build`

---

## 🔮 Next Steps

1. **Connect real API endpoints** in PodcastProcessor.tsx
2. **Test with actual Sieve and ElevenLabs APIs**
3. **Deploy to production** (Vercel + Railway/Heroku)
4. **Add authentication** if needed
5. **Implement file storage** (AWS S3/CloudFlare R2)

---

Ready to revolutionize podcast outreach! 🎯 