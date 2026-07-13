# Integration Guide: Wiring Existing Logic to Workers

This guide shows you exactly how to integrate your existing sourcing, verification, enrichment, and outreach code into the new automation system.

## 📋 Overview

Each worker function in `workers.py` corresponds to a step in your CLAUDE_AGENT mission:

| Worker | Purpose | Status |
|--------|---------|--------|
| `run_source()` | Ingest public records → SOURCED leads | TODO |
| `run_verify()` | Verify financial facts → VERIFIED leads | TODO |
| `run_trace()` | Enrich with contact info → ENRICHED leads | TODO |
| `run_outreach()` | Generate outreach drafts → QUEUED_OUTREACH | TODO |

---

## 1️⃣ Integration: `run_source()`

Replace with your existing sourcing logic:

```python
def run_source():
    """SOURCE worker: Ingest new raw records."""
    try:
        info("[WORKER] SOURCE started", queue="source")
        
        # YOUR EXISTING CODE HERE
        raw_records = fetch_all_county_records()
        
        leads = []
        for i, raw_record in enumerate(raw_records):
            try:
                lead = {
                    "id": str(uuid.uuid4()),
                    "source": {
                        "name": "county_records",
                        "url": raw_record.get("source_url"),
                        "raw_id": raw_record.get("id"),
                        "retrieved_at": datetime.utcnow().isoformat()
                    },
                    "claimant_name": raw_record.get("owner_name"),
                    "property_address": {
                        "line1": raw_record.get("address"),
                        "city": raw_record.get("city"),
                        "state": raw_record.get("state"),
                        "zip": raw_record.get("zip")
                    },
                    "surplus_amount": None,
                    "status": "SOURCED",
                    "created_at": datetime.utcnow().isoformat(),
                }
                
                insert_lead_to_db(lead)
                leads.append(lead)
                
                progress = ((i + 1) / len(raw_records)) * 100
                info(f"SOURCE progress: {progress:.1f}%", queue="source")
                
            except Exception as e:
                error(f"SOURCE failed for record {i}: {str(e)}", queue="source")
                continue
        
        info("[WORKER] SOURCE completed", queue="source")
        return {"status": "completed", "sourced_count": len(leads)}
    
    except Exception as e:
        error(f"[WORKER] SOURCE failed: {str(e)}", queue="source")
        raise
```

---

## 2️⃣ Integration: `run_verify()`

```python
def run_verify():
    """VERIFY worker: Apply verification rules."""
    try:
        info("[WORKER] VERIFY started", queue="verify")
        
        unverified_leads = fetch_leads_by_status("SOURCED")
        
        verified_count = 0
        for i, lead in enumerate(unverified_leads):
            try:
                verified_lead = verify_lead(lead)
                
                if verified_lead["sale_price"] and verified_lead["debt_amount"]:
                    surplus = verified_lead["sale_price"] - verified_lead["debt_amount"]
                    verified_lead["surplus_amount"] = max(0, surplus)
                
                confidence = calculate_verification_confidence(verified_lead)
                
                if confidence >= 0.6:
                    verified_lead["status"] = "VERIFIED"
                else:
                    verified_lead["status"] = "NEEDS_REVIEW"
                
                update_lead_in_db(verified_lead)
                verified_count += 1
                
                progress = ((i + 1) / len(unverified_leads)) * 100
                info(f"VERIFY progress: {progress:.1f}%", queue="verify")
                
            except Exception as e:
                error(f"VERIFY failed for lead {lead['id']}: {str(e)}", queue="verify")
                continue
        
        info("[WORKER] VERIFY completed", queue="verify")
        return {"status": "completed", "verified_count": verified_count}
    
    except Exception as e:
        error(f"[WORKER] VERIFY failed: {str(e)}", queue="verify")
        raise
```

---

## 3️⃣ Integration: `run_trace()`

```python
def run_trace():
    """TRACE worker: Enrich verified leads with contact info."""
    try:
        info("[WORKER] TRACE started", queue="trace")
        
        verified_leads = fetch_leads_by_status("VERIFIED")
        unenriched_leads = [l for l in verified_leads if not l.get("enrichment", {}).get("phone")]
        
        enriched_count = 0
        for i, lead in enumerate(unenriched_leads):
            try:
                enrichment_result = skip_trace_api_call(
                    name=lead["claimant_name"],
                    address=lead["property_address"]["line1"]
                )
                
                if enrichment_result:
                    lead["enrichment"] = {
                        "phone": {"value": enrichment_result.get("phone"), "source": "skip_trace"},
                        "email": {"value": enrichment_result.get("email"), "source": "skip_trace"},
                        "forwarding_address": {"value": enrichment_result.get("address"), "source": "skip_trace"}
                    }
                    lead["status"] = "ENRICHED"
                    
                    if enrichment_result.get("risk_flag"):
                        lead["status"] = "HIGH_RISK"
                
                update_lead_in_db(lead)
                enriched_count += 1
                
                progress = ((i + 1) / len(unenriched_leads)) * 100
                info(f"TRACE progress: {progress:.1f}%", queue="trace")
                
            except Exception as e:
                error(f"TRACE failed for lead {lead['id']}: {str(e)}", queue="trace")
                continue
        
        info("[WORKER] TRACE completed", queue="trace")
        return {"status": "completed", "enriched_count": enriched_count}
    
    except Exception as e:
        error(f"[WORKER] TRACE failed: {str(e)}", queue="trace")
        raise
```

---

## 4️⃣ Integration: `run_outreach()`

```python
def run_outreach():
    """OUTREACH worker: Generate outreach drafts."""
    try:
        info("[WORKER] OUTREACH started", queue="outreach")
        
        enriched_leads = fetch_leads_by_status("ENRICHED")
        
        outreach_count = 0
        for i, lead in enumerate(enriched_leads):
            try:
                outreach_draft = {
                    "lead_id": lead["id"],
                    "email": generate_email_body(lead),
                    "sms": generate_sms_body(lead),
                    "phone_script": generate_phone_script(lead),
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                queue_outreach_for_review(lead, outreach_draft)
                
                lead["status"] = "QUEUED_OUTREACH"
                update_lead_in_db(lead)
                outreach_count += 1
                
                progress = ((i + 1) / len(enriched_leads)) * 100
                info(f"OUTREACH progress: {progress:.1f}%", queue="outreach")
                
            except Exception as e:
                error(f"OUTREACH failed for lead {lead['id']}: {str(e)}", queue="outreach")
                continue
        
        info("[WORKER] OUTREACH completed", queue="outreach")
        return {"status": "completed", "outreach_count": outreach_count}
    
    except Exception as e:
        error(f"[WORKER] OUTREACH failed: {str(e)}", queue="outreach")
        raise
```

---

## 🛠️ Helper Functions

```python
from datetime import datetime
from uuid import uuid4

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_lead_to_db(lead):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leads (id, claimant_name, property_address, surplus_amount, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (lead["id"], lead["claimant_name"], str(lead["property_address"]), lead.get("surplus_amount"), lead["status"], lead["created_at"]))
    conn.commit()
    cur.close()
    conn.close()

def fetch_leads_by_status(status: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE status = %s", (status,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def update_lead_in_db(lead):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""UPDATE leads SET status = %s, surplus_amount = %s, updated_at = %s WHERE id = %s""",
                (lead["status"], lead.get("surplus_amount"), datetime.utcnow().isoformat(), lead["id"]))
    conn.commit()
    cur.close()
    conn.close()

def generate_email_body(lead) -> str:
    return f"Dear {lead['claimant_name']}, we found ${lead['surplus_amount']} in surplus funds from {lead['property_address']['line1']}..."

def generate_sms_body(lead) -> str:
    return f"Hi, we found ${lead['surplus_amount']} in unclaimed funds from your property. Reply for details."

def generate_phone_script(lead) -> str:
    return f"Hi {lead['claimant_name']}, calling about ${lead['surplus_amount']} in surplus funds..."

def queue_outreach_for_review(lead, outreach_draft):
    pass  # Mark for human approval before sending
```

---

## ✅ Testing

```bash
# Trigger SOURCE
curl -X POST http://localhost:8000/api/trigger/manual-run -H "Content-Type: application/json" -d '{"run_type": "source"}'

# Check logs
curl http://localhost:8000/api/logs?limit=50

# Check status
curl http://localhost:8000/api/status
```

Once integrated, your Surplus Hunter AI runs fully autonomously! 🚀
