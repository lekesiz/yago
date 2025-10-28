# YAGO Logs Directory

This directory contains application logs for local development.

## Log Files
- `backend.log` - Backend API logs (uvicorn)
- `frontend.log` - Frontend dev server logs (Vite)

## Viewing Logs
```bash
# Real-time backend logs
tail -f logs/backend.log

# Real-time frontend logs
tail -f logs/frontend.log

# Last 100 lines
tail -100 logs/backend.log
```

## Log Rotation
Logs are appended to these files. For production, consider using a proper log rotation system.

