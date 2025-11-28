# 📧 Email Alert Testing Guide

## Quick Test - Send Email Now!

### Step 1: Setup Gmail App Password (2 minutes)

**Why App Password?**  
Gmail blocks regular passwords for security. You need a special 16-character App Password.

**Get Your App Password:**
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already on)
3. Search for "App passwords" or go to: https://myaccount.google.com/apppasswords
4. Create new app password:
   - App: **Mail**
   - Device: **Windows Computer** (or any)
5. Copy the 16-character password (no spaces)

### Step 2: Add to `.env` File

Open your `.env` file and add/update these lines:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-16-char-app-password-here
FROM_EMAIL=your.email@gmail.com
FROM_NAME=Weather Disaster Management
```

**Example:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ramprasath.t@ideas2it.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Your 16-char app password
FROM_EMAIL=ramprasath.t@ideas2it.com
FROM_NAME=Weather Disaster Management
```

### Step 3: Restart Backend

```bash
# Press Ctrl+C in backend terminal, then restart:
uvicorn src.api.fastapi_app:app --reload
```

### Step 4: Test Email Sending

**Option A - Using Web UI (Easiest):**

1. Open browser: http://localhost:3000
2. Make sure you're logged in
3. Open browser console (F12)
4. Run this command in console:

```javascript
fetch('http://localhost:8000/alerts/test-email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({
    email: 'YOUR_EMAIL@gmail.com',  // Put your email here
    location: 'Jaffna Test'
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

**Option B - Using Postman:**

1. **POST** to: `http://localhost:8000/alerts/test-email`
2. **Headers:**
   ```
   Content-Type: application/json
   Authorization: Bearer YOUR_JWT_TOKEN
   ```
3. **Body (JSON):**
   ```json
   {
     "email": "your.email@gmail.com",
     "location": "Test Location"
   }
   ```

**Option C - Using curl:**

```bash
curl -X POST http://localhost:8000/alerts/test-email \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "email": "your.email@gmail.com",
    "location": "Test Location"
  }'
```

### Step 5: Check Results

**If Successful:**
```json
{
  "success": true,
  "message": "Test email sent successfully to your.email@gmail.com",
  "details": "Check your inbox (and spam folder) for the test alert email"
}
```

✅ **Check your email!** You should receive a beautiful HTML email with weather alert.

**If SMTP Not Configured:**
```json
{
  "success": false,
  "error": "SMTP not configured. Please set SMTP_USER and SMTP_PASSWORD in your .env file",
  "help": { ... }
}
```

❌ **Action:** Go back to Step 2 and add SMTP credentials to `.env`

**If Authentication Failed:**
```json
{
  "success": false,
  "error": "SMTP Authentication Failed",
  "help": {
    "gmail": "You need an App Password (not your regular password)"
  }
}
```

❌ **Action:** Go back to Step 1 and get Gmail App Password

---

## Troubleshooting

### Problem: "SMTP Authentication Failed"

**Cause:** Using regular password instead of App Password

**Solution:**
1. Get Gmail App Password (Step 1 above)
2. Make sure it's 16 characters (remove any spaces)
3. Update `.env` file
4. Restart backend

### Problem: "SMTP not configured"

**Cause:** Environment variables not set

**Solution:**
1. Open `.env` file in project root
2. Add all SMTP variables (Step 2 above)
3. Save file
4. Restart backend

### Problem: Email not received

**Check these:**
1. ✅ Check spam/junk folder
2. ✅ Verify email address is correct
3. ✅ Check backend logs for errors
4. ✅ Try sending to different email

### Problem: "User not found" or "Unauthorized"

**Cause:** Not logged in or invalid token

**Solution:**
1. Log in to web UI: http://localhost:3000
2. Go to browser console (F12)
3. Check if token exists: `localStorage.getItem('token')`
4. If no token, log in again

---

## What Happens After Email Works?

### 1. Real Alert System

Once email is working, the real alert system will:
1. Detect severe weather automatically
2. Create alerts in database
3. Find subscribed users
4. Send emails to all subscribers

### 2. Subscribe to Locations

Users can subscribe to get alerts for specific locations:

**Create Subscription:**
```bash
POST /alerts/subscriptions
{
  "location": "Jaffna",
  "radius_km": 50,
  "email_enabled": true,
  "notify_on_critical": true,
  "notify_on_high": true
}
```

### 3. Automatic Alerts

When disaster response detects severe weather:
```bash
POST /api/v1/disaster-response
{
  "location": "Jaffna"
}
```

If CRITICAL/HIGH conditions detected:
- Alert created in database
- Emails sent to all subscribers in that area
- Notifications logged

---

## Testing Real Alerts

### Step 1: Create Subscription

```javascript
// In browser console (while logged in):
fetch('http://localhost:8000/alerts/subscriptions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({
    location: 'Jaffna',
    radius_km: 50,
    email_enabled: true,
    notify_on_high: true,
    notify_on_critical: true
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

### Step 2: Check for Alerts

```javascript
// Check Jaffna weather and create alert if severe
fetch('http://localhost:8000/alerts/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({
    location: 'Jaffna'
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

If severe conditions detected, you'll get email automatically!

---

## Email Template Preview

The test email includes:
- ⚠️ **Alert Header** with severity color
- 📍 **Location Details**
- 🌡️ **Weather Conditions** (temp, wind, rain, humidity)
- 🛡️ **Safety Recommendations**
- 📧 **Professional Design** (HTML + plain text)

---

## Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Test Email | `/alerts/test-email` | POST |
| Create Subscription | `/alerts/subscriptions` | POST |
| List Subscriptions | `/alerts/subscriptions` | GET |
| Check for Alerts | `/alerts/check` | POST |
| List Alerts | `/alerts/` | GET |

---

## Need Help?

1. Check backend logs in terminal
2. Look for errors in `logs/disaster_management_*.log`
3. Verify `.env` file has correct values
4. Make sure backend restarted after changing `.env`

**Still stuck?** The test endpoint will give you specific error messages with solutions!

---

**🎉 Once email test works, your alert system is fully functional!**

