# README: Automation Dashboard Setup

## Quick Start

You now have a fully automated Surplus Hunter AI system with real-time monitoring!

### Files Added

**Backend:**
- `main.py` - FastAPI server with WebSocket & scheduler
- `queue.py` - RQ job queue
- `logger.py` - Logging system
- `scheduler.py` - Daily automation scheduler
- `workers.py` - Worker functions (TODO: wire your logic)
- `api_routes.py` - API endpoints
- `schemas.py` - Data models
- `websocket_manager.py` - WebSocket handler
- `requirements.txt` - Updated dependencies
- `.env.example` - Configuration template

**Frontend:**
- `Dashboard.tsx` - React dashboard

**Database:**
- `migrations/001_automation_tables.sql` - SQL migrations

**Documentation:**
- `INTEGRATION_GUIDE.md` - How to wire your existing code

### Setup (5 minutes)

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Start Redis
docker run -d -p 6379:6379 redis:latest

# 3. Run migrations
psql $DATABASE_URL < migrations/001_automation_tables.sql

# 4. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, etc.

# 5. Start servers
# Terminal 1: API
python -m uvicorn main:app --reload --port 8000

# Terminal 2: RQ Worker
rq worker source verify trace outreach

# 6. Open dashboard
# http://localhost:8000
```

### Next Steps

1. **Read `INTEGRATION_GUIDE.md`** - Shows exactly how to wire your sourcing/verify/trace/outreach logic
2. **Update `workers.py`** - Replace placeholder functions with your actual code
3. **Test locally** - Trigger manual runs, watch dashboard
4. **Deploy to production** - Push to Render + Supabase

### Dashboard Features

- ✅ Live queue status (Source, Verify, Trace, Outreach)
- ✅ Progress bars showing % complete
- ✅ Real-time activity log (auto-scrolling)
- ✅ Manual control buttons (full run or individual steps)
- ✅ Shows which lead is being processed
- ✅ Color-coded logs (INFO/WARNING/ERROR)

### Configuration

Edit `.env`:
```bash
DAILY_RUN_TIME=03:00          # 3 AM UTC daily
SCHEDULE_ENABLED=true         # Enable/disable scheduler
DATABASE_URL=...              # Your Supabase connection
REDIS_URL=redis://localhost   # Your Redis
```

### Need Help?

See `INTEGRATION_GUIDE.md` for detailed examples of:
- How to wire SOURCE (fetching records)
- How to wire VERIFY (verifying leads)
- How to wire TRACE (enriching with contact info)
- How to wire OUTREACH (generating drafts)

**Your AI is now fully automated with visual monitoring!** 🚀
