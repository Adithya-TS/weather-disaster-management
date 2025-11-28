# Alerts & Notifications System - Workflow Diagram

## 🔄 Current Implementation: MANUAL TRIGGER

The system is currently **MANUAL** - alerts are created when explicitly requested.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MANUAL ALERT WORKFLOW (Current)                      │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   User/Admin │
│   Actions    │
└──────┬───────┘
       │
       │ 1. Triggers check for location
       ▼
┌─────────────────────────────┐
│  POST /alerts/check         │
│  { location: "Chennai" }    │
└──────────┬──────────────────┘
           │
           │ 2. Analyzes weather data
           ▼
┌─────────────────────────────┐
│   Alert Service             │
│   • Get weather data        │
│   • Check thresholds        │
│   • Detect severe conditions│
└──────────┬──────────────────┘
           │
           ├─── NO severe weather ─→ Return "No alerts"
           │
           └─── SEVERE weather detected
                │
                ▼
         ┌─────────────────────┐
         │  Create Alert       │
         │  • Type: Hurricane  │
         │  • Severity: CRITICAL│
         │  • Location: Chennai│
         └──────────┬──────────┘
                    │
                    │ 3. Alert saved to database
                    ▼
         ┌─────────────────────────┐
         │  Find Subscribed Users  │
         │  • Search by location   │
         │  • Check radius         │
         └──────────┬──────────────┘
                    │
                    │ 4. Get matching users
                    ▼
         ┌─────────────────────────┐
         │  Notification Service   │
         │  • Filter by preferences│
         │  • Generate emails      │
         └──────────┬──────────────┘
                    │
                    │ 5. Send emails
                    ▼
         ┌─────────────────────────┐
         │  📧 Email Sent          │
         │  • Beautiful HTML       │
         │  • Alert details        │
         │  • Safety info          │
         └──────────┬──────────────┘
                    │
                    │ 6. Log notification
                    ▼
         ┌─────────────────────────┐
         │  Notification Log       │
         │  • Status: SENT         │
         │  • Timestamp            │
         └─────────────────────────┘
```

---

## 🤖 AUTOMATIC WORKFLOW (Future Enhancement)

This is what you should implement for true automation:

```
┌─────────────────────────────────────────────────────────────────────────┐
│              AUTOMATIC ALERT WORKFLOW (Recommended)                     │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   Background Scheduler   │
│   (Runs every 30 min)    │
└──────────┬───────────────┘
           │
           │ Triggers automatically
           ▼
┌─────────────────────────────────┐
│  Get All Active Subscriptions   │
│  • Query database               │
│  • Get unique locations         │
└──────────┬──────────────────────┘
           │
           │ List: ["Chennai", "Mumbai", "Delhi", ...]
           ▼
┌─────────────────────────────────┐
│   For Each Location:            │
│   Loop Through All Cities       │
└──────────┬──────────────────────┘
           │
           │ For "Chennai"
           ▼
┌─────────────────────────────────┐
│   Check Weather for Location    │
│   • Fetch latest weather data   │
│   • Analyze conditions          │
│   • Compare with thresholds     │
└──────────┬──────────────────────┘
           │
           ├─── Normal conditions ──→ Skip, continue to next
           │
           └─── SEVERE conditions detected!
                │
                ▼
         ┌──────────────────────┐
         │  Create Alert        │
         │  (if not exists)     │
         └──────┬───────────────┘
                │
                │ Check: Similar alert in last 6 hours?
                │
                ├─── YES ──→ Skip (prevent spam)
                │
                └─── NO ──→ Create new alert
                           │
                           ▼
                    ┌──────────────────────┐
                    │  Save to Database    │
                    │  • Alert created     │
                    │  • is_sent = False   │
                    └──────┬───────────────┘
                           │
                           │ Trigger notifications
                           ▼
                    ┌──────────────────────────┐
                    │  Find Affected Users     │
                    │  • Match by location     │
                    │  • Check radius          │
                    │  • Filter by preferences │
                    └──────┬───────────────────┘
                           │
                           │ Found 150 users
                           ▼
                    ┌──────────────────────────┐
                    │  Send Notifications      │
                    │  • Batch email sending   │
                    │  • Rate limiting         │
                    └──────┬───────────────────┘
                           │
                           │ Success!
                           ▼
                    ┌──────────────────────────┐
                    │  Update Alert            │
                    │  • is_sent = True        │
                    │  • sent_at = now()       │
                    └──────────────────────────┘
```

---

## 📱 USER SUBSCRIPTION WORKFLOW

How users set up to receive alerts:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      USER SUBSCRIPTION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   User       │
│   Login      │
└──────┬───────┘
       │
       │ 1. Navigate to Alerts page
       ▼
┌─────────────────────────────┐
│  Alerts & Notifications UI  │
│  • View active alerts       │
│  • Manage subscriptions     │
└──────────┬──────────────────┘
           │
           │ 2. Click "Add Subscription"
           ▼
┌─────────────────────────────────────┐
│  Subscription Form                  │
│  ┌─────────────────────────────┐   │
│  │ Location: Chennai           │   │
│  │ Radius: 50 km              │   │
│  │ ☑ Email notifications       │   │
│  │                             │   │
│  │ Severity Levels:            │   │
│  │ ☑ CRITICAL                  │   │
│  │ ☑ HIGH                      │   │
│  │ ☑ MEDIUM                    │   │
│  │ ☐ LOW                       │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           │ 3. Save subscription
           ▼
┌─────────────────────────────┐
│  POST /alerts/subscriptions │
│  Backend validates & saves  │
└──────────┬──────────────────┘
           │
           │ 4. Geocode location
           ▼
┌─────────────────────────────┐
│  Get Coordinates            │
│  • Lat: 13.0827             │
│  • Lon: 80.2707             │
│  • City: Chennai            │
│  • State: Tamil Nadu        │
└──────────┬──────────────────┘
           │
           │ 5. Save to database
           ▼
┌─────────────────────────────────────┐
│  user_subscriptions table           │
│  ┌───────────────────────────────┐ │
│  │ user_id: 123                  │ │
│  │ location: Chennai             │ │
│  │ radius_km: 50                 │ │
│  │ notify_on_critical: true      │ │
│  │ email_enabled: true           │ │
│  │ is_active: true               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
           │
           │ ✅ Subscription Active!
           ▼
┌─────────────────────────────────────┐
│  User will now receive alerts when │
│  severe weather detected in Chennai │
│  within 50km radius                 │
└─────────────────────────────────────┘
```

---

## 📧 EMAIL NOTIFICATION FLOW

How emails are generated and sent:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EMAIL NOTIFICATION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Alert Created       │
│  Location: Chennai   │
│  Severity: CRITICAL  │
└──────┬───────────────┘
       │
       │ 1. Find subscribed users
       ▼
┌─────────────────────────────────────┐
│  Query user_subscriptions           │
│  WHERE location LIKE '%Chennai%'    │
│  AND is_active = true               │
└──────────┬──────────────────────────┘
           │
           │ Found: User A, User B, User C
           ▼
┌─────────────────────────────────────┐
│  For Each User: Check Preferences   │
│  ┌─────────────────────────────┐   │
│  │ User A:                     │   │
│  │ • notify_on_critical: ✅    │   │
│  │ • email_enabled: ✅         │   │
│  │ ➜ SEND EMAIL              │   │
│  │                             │   │
│  │ User B:                     │   │
│  │ • notify_on_critical: ✅    │   │
│  │ • email_enabled: ❌         │   │
│  │ ➜ SKIP                     │   │
│  │                             │   │
│  │ User C:                     │   │
│  │ • notify_on_critical: ❌    │   │
│  │ ➜ SKIP                     │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           │ For User A
           ▼
┌─────────────────────────────────────┐
│  Generate Email Content             │
│  • HTML template with styling       │
│  • Plain text version               │
│  • Include weather details          │
│  • Add safety recommendations       │
└──────────┬──────────────────────────┘
           │
           │ Email ready
           ▼
┌─────────────────────────────────────┐
│  Send via SMTP                      │
│  • Connect to Gmail (smtp.gmail.com)│
│  • Authenticate                      │
│  • Send message                      │
└──────────┬──────────────────────────┘
           │
           ├─── SUCCESS ───┐
           │               │
           │               ▼
           │        ┌──────────────────────┐
           │        │  Log Notification    │
           │        │  • status: SENT      │
           │        │  • sent_at: now()    │
           │        └──────────────────────┘
           │
           └─── FAILED ────┐
                           │
                           ▼
                    ┌──────────────────────┐
                    │  Log Notification    │
                    │  • status: FAILED    │
                    │  • error_message     │
                    └──────────────────────┘
```

---

## 🎯 COMPLETE END-TO-END FLOW

Full system workflow from setup to notification:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE SYSTEM WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────┘


STEP 1: USER SETUP
════════════════════════════════════════════════════════════════════
👤 User Login
   └─→ 🔑 JWT Token Generated
        └─→ 📱 Navigate to Alerts Page
             └─→ ➕ Create Subscription
                  └─→ 💾 Saved to Database
                       └─→ ✅ User subscribed to Chennai


STEP 2: ALERT DETECTION (Manual or Automatic)
════════════════════════════════════════════════════════════════════

MANUAL (Current):
━━━━━━━━━━━━━━━━━
👤 Admin/User → POST /alerts/check → Analyze Weather → Create Alert


AUTOMATIC (Recommended):
━━━━━━━━━━━━━━━━━━━━━━━
⏰ Scheduler (Every 30 min)
   └─→ 📍 Get All Subscribed Locations
        └─→ 🌡️ Check Weather for Each
             └─→ ⚠️ If Severe → Create Alert
                  

STEP 3: WEATHER ANALYSIS
════════════════════════════════════════════════════════════════════
🌍 Fetch Weather Data (OpenWeather API)
   └─→ 📊 Extract Metrics:
        • Temperature: 45°C
        • Wind Speed: 125 km/h
        • Precipitation: 120mm
        • Humidity: 95%
   
   └─→ ⚖️ Compare with Thresholds:
        Temperature 45°C ≥ 40°C → ⚠️ HEATWAVE CRITICAL
        Wind 125 km/h ≥ 118 km/h → ⚠️ HURRICANE CRITICAL
        Rain 120mm ≥ 100mm → ⚠️ FLOOD CRITICAL


STEP 4: ALERT CREATION
════════════════════════════════════════════════════════════════════
🚨 Create Alert Object:
   ├─ Type: HURRICANE
   ├─ Severity: CRITICAL
   ├─ Location: Chennai
   ├─ Description: "Hurricane Force Winds Detected..."
   └─ Weather Data: [temp, wind, rain, humidity]

   └─→ 💾 Save to alerts table
        └─→ 🔍 Check for duplicates (last 6 hours)
             ├─ Found → Skip (prevent spam)
             └─ Not found → Save new alert


STEP 5: USER MATCHING
════════════════════════════════════════════════════════════════════
🔍 Search user_subscriptions:
   WHERE (location LIKE '%Chennai%' 
      OR city LIKE '%Chennai%')
   AND is_active = true

   Found: 150 users subscribed


STEP 6: PREFERENCE FILTERING
════════════════════════════════════════════════════════════════════
👥 150 Users → Filter by preferences:
   
   User 1: notify_on_critical ✅, email_enabled ✅ → SEND ✓
   User 2: notify_on_critical ✅, email_enabled ❌ → SKIP
   User 3: notify_on_critical ❌ → SKIP
   ...
   
   Result: 89 users will receive email


STEP 7: EMAIL GENERATION
════════════════════════════════════════════════════════════════════
📧 For each of 89 users:
   
   ┌────────────────────────────────────┐
   │ To: user@example.com              │
   │ Subject: 🚨 CRITICAL ALERT        │
   │                                    │
   │ Hi John,                           │
   │                                    │
   │ Hurricane Force Winds Detected    │
   │ Location: Chennai, Tamil Nadu     │
   │ Severity: CRITICAL                │
   │                                    │
   │ Weather Conditions:               │
   │ • Wind: 125 km/h                  │
   │ • Temp: 45°C                      │
   │                                    │
   │ Safety Recommendations:           │
   │ • Seek shelter immediately        │
   │ • Stay away from windows          │
   │ ...                                │
   └────────────────────────────────────┘


STEP 8: EMAIL SENDING
════════════════════════════════════════════════════════════════════
📤 Batch Send via SMTP:
   
   Connect → smtp.gmail.com:587
   Auth → SMTP_USER / SMTP_PASSWORD
   
   Send Email 1 → ✅ Success
   Send Email 2 → ✅ Success
   Send Email 3 → ❌ Failed (invalid email)
   ...
   Send Email 89 → ✅ Success
   
   Results: 88 sent, 1 failed


STEP 9: LOGGING
════════════════════════════════════════════════════════════════════
💾 Save to notification_logs:
   
   For each email:
   ├─ user_id
   ├─ alert_id
   ├─ type: EMAIL
   ├─ status: SENT / FAILED
   ├─ sent_at: timestamp
   └─ error_message: (if failed)


STEP 10: ALERT UPDATE
════════════════════════════════════════════════════════════════════
✅ Update alert:
   └─→ is_sent = true
        └─→ sent_at = current_timestamp


COMPLETE! 🎉
════════════════════════════════════════════════════════════════════
✅ Alert created
✅ Users notified
✅ Emails sent
✅ Logs recorded
```

---

## ⚙️ HOW TO IMPLEMENT AUTOMATIC MONITORING

To enable automatic weather monitoring, add this code:

### Option 1: Using APScheduler (Python)

```python
# In src/api/fastapi_app.py (at startup)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def check_all_locations_for_alerts():
    """Background task to check weather for all subscribed locations"""
    from sqlalchemy import select, func
    from .models import UserSubscription
    from .services.alert_service import AlertService
    from .services.notification_service import NotificationService
    
    async with AsyncSessionLocal() as db:
        # Get unique locations
        stmt = select(
            func.distinct(UserSubscription.location)
        ).where(UserSubscription.is_active == True)
        
        result = await db.execute(stmt)
        locations = result.scalars().all()
        
        alert_service = AlertService(db)
        notification_service = NotificationService(db)
        
        for location in locations:
            # Check for alerts
            alert_data = await alert_service.analyze_weather_for_alerts(location)
            
            if alert_data:
                # Create alert
                alert = await alert_service.create_alert(alert_data)
                
                # Send notifications
                await notification_service.send_alert_notifications(alert)

# Schedule to run every 30 minutes
scheduler.add_job(
    check_all_locations_for_alerts,
    'interval',
    minutes=30,
    id='weather_monitor'
)

@app.on_event("startup")
async def startup_event():
    scheduler.start()
    logger.info("Scheduler started - monitoring every 30 minutes")
```

### Option 2: Using Cron Job (System Level)

```bash
# Create a script: scripts/check_alerts.py
# Then add to crontab:

*/30 * * * * cd /path/to/project && ./venv/bin/python scripts/check_alerts.py
```

---

## 📊 COMPARISON: MANUAL vs AUTOMATIC

| Feature | MANUAL (Current) | AUTOMATIC (Recommended) |
|---------|------------------|------------------------|
| **Trigger** | User/Admin must call API | Runs automatically on schedule |
| **Coverage** | Only checked locations | All subscribed locations |
| **Frequency** | On-demand | Every 30 minutes |
| **Reliability** | Depends on manual action | Guaranteed monitoring |
| **Scalability** | Limited | Handles 1000s of locations |
| **Real-time** | Only when triggered | Near real-time (30 min delay) |
| **Setup** | Already working | Needs scheduler setup |

---

## 🎯 RECOMMENDED IMPLEMENTATION

**BEST APPROACH: Hybrid System**

1. **Automatic Background Monitoring** (Every 30 min)
   - Continuously monitors all subscribed locations
   - Creates alerts for severe weather
   - Sends notifications automatically

2. **Manual Check** (On-demand)
   - Allow users/admins to force immediate check
   - Useful for urgent situations
   - Good for testing

3. **User Subscriptions** (Self-service)
   - Users manage their own preferences
   - Subscribe to multiple locations
   - Control notification levels

---

## 📝 SUMMARY

### Current System: ✅ MANUAL
- Works perfectly for on-demand checks
- User triggers: POST /alerts/check
- Great for testing and demonstration

### Recommended: 🤖 AUTOMATIC
- Add background scheduler
- Monitors continuously
- True disaster management system
- Production-ready

### Both approaches work together:
```
AUTOMATIC (background) + MANUAL (on-demand) = COMPLETE SYSTEM
```

---

See `ALERTS_SETUP_GUIDE.md` for implementation details!

