# Quick Start Guide - IT Ops Agent System

Get up and running in 5 minutes! This is a condensed version of the full [RUN_GUIDE.md](RUN_GUIDE.md).

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] OpenAI API key ready
- [ ] Docker installed (for Chroma DB)

## 5-Minute Setup

### Step 1: Clone and Setup (1 minute)

```bash
# Navigate to your project directory
cd "C:\AI Projects\Agentic AI\ITOps PoC v3"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (1 minute)

Create a `.env` file in the project root:

**Windows (PowerShell):**
```powershell
"OPENAI_API_KEY=your_openai_api_key_here" | Out-File -FilePath .env -Encoding utf8
```

**Linux/Mac:**
```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

**Or manually create `.env` file with:**
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Start Chroma DB (1 minute)

```bash
cd docker
docker-compose up -d chroma
cd ..
```

Wait about 10-20 seconds for Chroma to start, then verify:
```bash
curl http://localhost:8000/api/v1/heartbeat
```

### Step 4: Load Instructions (1 minute)

```bash
python scripts/load_instructions.py
```

Should see: `Loaded 23/23 instruction(s) successfully`

### Step 5: Run the App (1 minute)

```bash
python -m src.api.gradio_app
```

### Step 6: Access in Browser

Open: **http://localhost:7860**

## Test It!

Try this query in the chat interface:
```
Reset password for user john.doe in AWS IAM
```

Make sure **Dry Run Mode** is enabled to see commands without executing.

## Troubleshooting

**Chroma not starting?**
```bash
docker ps  # Check if container is running
docker-compose logs chroma  # Check logs
```

**Can't connect to Chroma?**
```bash
# Wait a bit longer for Chroma to start (30-60 seconds)
curl http://localhost:8000/api/v1/heartbeat
```

**Import errors?**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Port 7860 already in use?**
Change port in `.env`:
```env
APP_PORT=7861
```

## What's Next?

- ✅ **Detailed Setup:** See [RUN_GUIDE.md](RUN_GUIDE.md) for comprehensive instructions
- ✅ **Testing:** See [TESTING.md](TESTING.md) for testing procedures
- ✅ **Usage:** See [USER_GUIDE.md](USER_GUIDE.md) for usage examples
- ✅ **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md) for system design

## Quick Commands Reference

```bash
# Start Chroma
cd docker && docker-compose up -d chroma && cd ..

# Load instructions
python scripts/load_instructions.py

# Run app
python -m src.api.gradio_app

# Run tests
pytest

# Stop Chroma
cd docker && docker-compose down && cd ..
```

---

**That's it! You're ready to go! 🎉**

