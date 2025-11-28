# ✅ Send Alerts Button - FIXED!

## Problem
When clicking "Send Alerts" button, the system was only simulating alerts (showing text) but NOT sending real emails.

## Root Cause
The `/api/v1/alerts` endpoint was calling `send_emergency_alerts()` which only returned simulated text, not actual email delivery.

## Solution Implemented

### 1. Backend Fixed (`src/api/fastapi_app.py`)

**Updated `/api/v1/alerts` endpoint to:**

- **Option 1:** Send directly to user's email (specified in `send_to_email` field)
- **Option 2:** Send to all subscribers of active alerts
- **Option 3:** Fall back to simulation if no emails can be sent

**New request model:**
```python
class AlertRequest(BaseModel):
    response_plan: str  # The response plan content
    channels: Optional[List[str]]  # Alert channels
    location: Optional[str]  # Location for the alert
    send_to_email: Optional[str]  # Direct email (bypasses subscriptions)
```

### 2. Frontend Fixed (`frontend/src/pages/ResponsePlan.jsx`)

**Updated `handleSendAlerts()` to:**

- Get current user's email from localStorage (`auth_user`)
- Pass email to backend via `send_to_email` field
- Pass location from workflow data
- Show appropriate success message based on response

### 3. Email Delivery

**When you click "Send Alerts" now:**

1. ✅ Gets your email from login session
2. ✅ Sends **REAL EMAIL** with the response plan
3. ✅ Beautiful HTML email format
4. ✅ Includes all plan details
5. ✅ Shows success message with recipient

## How to Test

### Step 1: Make Sure SMTP is Configured

Add to your `.env` file:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your.email@gmail.com
```

### Step 2: Restart Backend

```bash
# Press Ctrl+C, then:
uvicorn src.api.fastapi_app:app --reload
```

### Step 3: Test the Button

1. Go to http://localhost:3000
2. Login with Google
3. Run disaster analysis for any location (e.g., "Jaffna")
4. View the Response Plan
5. Click **"Send Alerts"**
6. Select channels (email, sms, etc.)
7. Click **"Send Alerts"** in the modal

### Step 4: Check Results

**Success Response:**
```json
{
  "success": true,
  "email_notifications_sent": true,
  "emails_sent": 1,
  "recipient": "your.email@gmail.com",
  "message": "✅ Response plan email sent to your.email@gmail.com"
}
```

**Check your email!** You should receive:
- Subject: "🚨 EMERGENCY RESPONSE PLAN: [Location]"
- Full response plan in beautiful HTML format
- Safety recommendations
- Timestamp

## What's in the Email?

The email includes:
- 🚨 **Emergency header** (red alert style)
- 📋 **Complete response plan** 
- 📍 **Location details**
- ⚠️ **Warning about following local authorities**
- ⏰ **Timestamp**
- 💼 **Professional HTML design**

## Response Scenarios

### Scenario 1: Email Sent Successfully ✅
```json
{
  "success": true,
  "email_notifications_sent": true,
  "emails_sent": 1,
  "recipient": "user@example.com",
  "message": "✅ Response plan email sent to user@example.com"
}
```

### Scenario 2: SMTP Not Configured ⚠️
```json
{
  "success": false,
  "error": "SMTP not configured",
  "message": "⚠️ Email cannot be sent - SMTP credentials not set",
  "note": "Set SMTP_USER and SMTP_PASSWORD in .env"
}
```

### Scenario 3: No Subscribers (Fallback) 📋
```json
{
  "success": true,
  "email_notifications_sent": false,
  "message": "⚠️ No active alerts or subscribers",
  "simulation_result": "ALERT DISTRIBUTION STATUS...",
  "note": "Showing simulated distribution"
}
```

## Frontend Changes

### Before:
```javascript
await sendAlerts({
  response_plan: workflowData.response_plan,
  channels: alertChannels,
});
// No email sent - just simulation
```

### After:
```javascript
// Get user email from localStorage
const authUser = localStorage.getItem('auth_user');
const user = JSON.parse(authUser);
const userEmail = user.email;

await sendAlerts({
  response_plan: workflowData.response_plan,
  channels: alertChannels,
  location: workflowData.location,
  send_to_email: userEmail  // ← NEW! Send to current user
});
// ✅ Real email delivered!
```

## Backend Flow

```
1. User clicks "Send Alerts" button
   ↓
2. Frontend sends request with user's email
   ↓
3. Backend receives request at /api/v1/alerts
   ↓
4. Checks if send_to_email is provided
   ↓
5. Creates email with response plan
   ↓
6. Sends via SMTP
   ↓
7. Returns success response
   ↓
8. Frontend shows success message
   ↓
9. User receives email!
```

## Troubleshooting

### Issue: "SMTP not configured"

**Fix:**
1. Add SMTP credentials to `.env`
2. For Gmail, use App Password
3. Restart backend

### Issue: "Authentication Failed"

**Fix:**
1. Get Gmail App Password: https://myaccount.google.com/apppasswords
2. Use 16-character password (not regular password)
3. Update `SMTP_PASSWORD` in `.env`

### Issue: No email received

**Check:**
1. ✅ Spam/junk folder
2. ✅ Backend logs for errors
3. ✅ SMTP credentials correct
4. ✅ User is logged in (email available)

### Issue: "Alerts sent successfully (simulated)"

**Reason:** No email address available or SMTP not configured

**Fix:**
1. Make sure you're logged in
2. Check SMTP configuration
3. Verify `.env` file

## Advanced: Send to Subscribers

If you don't want to send to the current user, but to all subscribers:

1. Remove `send_to_email` from the request
2. Make sure there are active alerts for the location
3. Users must be subscribed to that location
4. System will email all subscribers automatically

**Example:**
```javascript
await sendAlerts({
  response_plan: workflowData.response_plan,
  channels: alertChannels,
  location: "Jaffna",
  // No send_to_email - will send to subscribers
});
```

## Summary

| Feature | Before | After |
|---------|--------|-------|
| **Email Delivery** | ❌ Simulated only | ✅ Real emails sent |
| **Recipient** | ❌ None | ✅ Current user |
| **Content** | ❌ Just text | ✅ HTML email with plan |
| **SMTP** | ❌ Not used | ✅ Gmail/SMTP used |
| **Success Message** | Generic | Specific with recipient |

---

**🎉 Send Alerts button now sends REAL EMAILS with the response plan!**

**Test it now:**
1. Make sure SMTP configured in `.env`
2. Restart backend
3. Login to web UI
4. Analyze a disaster
5. Click "Send Alerts"
6. Check your email!

