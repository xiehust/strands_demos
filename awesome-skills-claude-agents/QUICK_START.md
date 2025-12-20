# Quick Start Guide

## 🚀 Starting the Platform

```bash
./start.sh
```

This will:
- ✅ Check and install dependencies
- ✅ Create `.env` from `.env.example` (if missing)
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:5173
- ✅ Save logs to `logs/` directory

**⚠️ Important**: After first run, edit `backend/.env` and add your `ANTHROPIC_API_KEY`

## 🛑 Stopping the Platform

```bash
./stop.sh
```

## 🔄 Restarting the Platform

```bash
./restart.sh
```

## 📊 Check Status

```bash
./status.sh
```

Shows:
- Process status (running/stopped)
- Port availability
- Log file locations and sizes
- Quick command reference

## 📝 View Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Both logs
tail -f logs/*.log
```

## 🌐 Access Points

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Or just run stop script
./stop.sh
```

### Services Not Starting

1. Check logs: `tail -f logs/backend.log` or `tail -f logs/frontend.log`
2. Verify `.env` file exists with `ANTHROPIC_API_KEY`
3. Ensure dependencies are installed:
   - Backend: `cd backend && source .venv/bin/activate && uv pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`

### Clean Restart

```bash
# Stop everything
./stop.sh

# Clean up PIDs and logs
rm -rf .pids logs

# Start fresh
./start.sh
```

## 📚 Documentation

- **CLAUDE.md** - Comprehensive guide for Claude Code
- **README.md** - Full project documentation
- **ARCHITECTURE.md** - System architecture details
- **backend/.env.example** - Environment variables template

## 💡 Common Tasks

### Update Dependencies

```bash
# Backend
cd backend
source .venv/bin/activate
uv pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Run Tests

```bash
# Frontend tests
cd frontend
npm run test
```

### Build for Production

```bash
# Frontend
cd frontend
npm run build

# Preview production build
npm run preview
```
