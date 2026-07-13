# Automation Dashboard & Scheduler Integration

## 🎯 Overview

This PR adds a **fully automated job queue system** with a **real-time React dashboard** to Surplus Hunter AI. The system runs the daily RUN CYCLE (source → verify → trace → outreach) autonomously and provides live visibility into agent activities.

## ✨ What's New

### Backend Infrastructure
- **RQ + Redis Job Queue**: Reliable, persistent job queueing with retry logic
- **APScheduler**: Cron-based daily automation (configurable time)
- **WebSocket Real-time Updates**: Live logs and progress tracking
- **Enhanced Logging**: All agent activities logged to database
- **API Monitoring Endpoints**: Track queue status and retrieve logs

### Frontend Dashboard
- **Live Status Cards**: Real-time job queue counts with progress bars
- **Activity Log**: Auto-scrolling, color-coded log stream
- **Manual Controls**: Trigger full runs or individual steps on demand
- **Current Processing**: Shows which lead is being actively processed
- **Responsive Design**: Tailwind CSS, works on mobile/desktop

### Database
- **Jobs Table**: Track automation runs with status, progress, timestamps
- **Logs Table**: Immutable audit trail of all agent activities
- **Indexed Queries**: Fast lookups by status, timestamp, job_id

## 📁 File Structure

```
project/
├── main.py                      # Updated FastAPI with WebSocket & scheduler
├── queue.py                     # RQ queue setup
├── logger.py                    # DB + console logging
├── scheduler.py                 # Daily scheduler & manual triggers
├── workers.py                   # Worker functions (TODO: wire your logic)
├── api_routes.py               # /api/status, /api/logs, /api/trigger endpoints
├── schemas.py                  # Pydantic models
├── websocket_manager.py        # WebSocket connection manager
├── Dashboard.tsx               # React dashboard component
├── migrations/
│   └── 001_automation_tables.sql
├── requirements.txt            # Updated dependencies
└── .env.example               # Configuration template
```

## 🚀 Deployment

### Prerequisites
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis
docker run -d -p 6379:6379 redis:latest

# 3. Run migrations
psql $DATABASE_URL < migrations/001_automation_tables.sql

# 4. Configure .env
cp .env.example .env
# Fill in: DATABASE_URL, REDIS_URL, DAILY_RUN_TIME, etc.
```

### Running the System
```bash
# Terminal 1: API Server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: RQ Worker
rq worker source verify trace outreach --with-scheduler

# Terminal 3: Access dashboard at http://localhost:8000
```

## 🔧 Integration: Wire Your Existing Logic

The `workers.py` file has placeholder functions. Replace with your actual logic:

### Example: Sourcing Worker
```python
# Current placeholder:
def run_source():
    info("[WORKER] SOURCE started", queue="source")
    return {"status": "completed", "sourced_count": 0}

# Your implementation:
def run_source():
    info("[WORKER] SOURCE started", queue="source")
    
    # Your existing sourcing logic here
    leads = fetch_public_records()  # Your function
    
    for i, lead in enumerate(leads):
        # Store lead in DB
        insert_lead_to_db(lead)
        
        # Emit progress
        progress = (i / len(leads)) * 100
        info(f"Processed {i}/{len(leads)}", queue="source")
    
    info("[WORKER] SOURCE completed", queue="source")
    return {"status": "completed", "sourced_count": len(leads)}
```

### Similar Pattern for `run_verify()`, `run_trace()`, `run_outreach()`

## 📊 How It Works

1. **Daily Cycle** (03:00 UTC by default):
   - Scheduler enqueues SOURCE job → waits for completion
   - Enqueues VERIFY job → waits
   - Enqueues TRACE job → waits
   - Enqueues OUTREACH job → waits

2. **RQ Workers** process queued jobs:
   - Log progress to database
   - Return completion status

3. **API Server** exposes:
   - `/api/status` - Queue counts and progress
   - `/api/logs` - Activity stream
   - `/api/trigger/manual-run` - Trigger runs on demand
   - `/ws` - WebSocket for real-time updates

4. **Dashboard** subscribes to WebSocket:
   - Receives progress updates
   - Displays live activity log
   - Shows current lead being processed

## 🎮 Control Panel

**Buttons in Dashboard:**
- ▶️ **Full RUN CYCLE**: Queues all 4 steps
- 🔍 **Source Only**: Queues SOURCE step
- ✓ **Verify Only**: Queues VERIFY step
- 🔎 **Trace Only**: Queues TRACE step

## 📋 Configuration (`.env`)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/surplus_hunter

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_PORT=8000
API_HOST=0.0.0.0

# Automation Schedule
SCHEDULE_ENABLED=true
DAILY_RUN_TIME=03:00  # HH:MM UTC format

# Contacts
OPERATOR_EMAIL=operator@example.com
LEGAL_REVIEW_EMAIL=legal@example.com
```

## 🔍 Monitoring

### View Logs
```bash
curl http://localhost:8000/api/logs?limit=50
```

### Get Queue Status
```bash
curl http://localhost:8000/api/status
```

### Trigger Manual Run
```bash
curl -X POST http://localhost:8000/api/trigger/manual-run \
  -H "Content-Type: application/json" \
  -d '{"run_type": "full"}'
```

## 🎯 Next Steps

1. **Wire your existing logic** into `workers.py` functions
2. **Test locally** with sample data
3. **Deploy to staging** (Render + Supabase)
4. **Monitor dashboa** for activity
5. **Configure production schedule** (DAILY_RUN_TIME, SCHEDULE_ENABLED)

## ⚠️ Important Notes

- **Human-in-the-loop**: Update `run_outreach()` to queue for human review, not auto-send
- **Error Handling**: All exceptions logged; jobs retry automatically
- **Scaling**: RQ workers can run on separate machines
- **Database**: Ensure `logs` table exists (migration included)

## ✅ Testing Checklist

- [ ] Redis running
- [ ] Migrations applied to Supabase
- [ ] `.env` configured correctly
- [ ] API server starts without errors
- [ ] Dashboard loads at `http://localhost:8000`
- [ ] WebSocket connects (check browser console)
- [ ] Manual run triggers successfully
- [ ] Logs appear in real-time
- [ ] Worker functions process jobs

---

**Ready to merge once you've wired your existing logic and tested locally.**
