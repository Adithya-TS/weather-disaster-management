# 🚀 Test Send Alerts Button - Quick Guide

## ⚡ 3-Step Test (2 Minutes)

### Step 1: Update .env (if not done)

Add these lines to `.env`:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=prasathram387@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=prasathram387@gmail.com
```

**Get App Password:** https://myaccount.google.com/apppasswords

### Step 2: Restart Backend

```bash
# Press Ctrl+C in backend terminal, then:
uvicorn src.api.fastapi_app:app --reload
```

Wait for: `Application startup complete.`

### Step 3: Click Send Alerts!

1. **Open:** http://localhost:3000
2. **Login** with Google (if not already)
3. **Analyze location:** Enter "Jaffna" and click "Analyze Disaster"
4. **View Response Plan** (you should see the plan)
5. **Click "Send Alerts"** button (top right)
6. **Select channels** (email, sms, etc.)
7. **Click "Send Alerts"** in modal

### Step 4: Check Email!

- ✅ Check inbox: prasathram387@gmail.com
- ✅ Check spam folder
- ✅ Look for: "🚨 EMERGENCY RESPONSE PLAN: Jaffna"

---

## What You'll See

### Success Message (Frontend):
```
✅ Email alert sent to prasathram387@gmail.com! Check your inbox.
```

### Email Content:
- **Subject:** 🚨 EMERGENCY RESPONSE PLAN: Jaffna
- **From:** Weather Disaster Management
- **Content:** 
  - Full response plan
  - Emergency instructions
  - Location details
  - Timestamp
  - Beautiful HTML formatting

---

## What Changed?

### Before ❌
- Button did nothing
- No API call made
- Just simulated alerts

### After ✅
- Button sends real email
- API call to `/api/v1/alerts`
- SMTP delivery via Gmail
- Response plan delivered to your inbox

---

## Troubleshooting

### "SMTP not configured"
→ Add SMTP credentials to `.env` and restart backend

### "Authentication Failed"
→ Use Gmail App Password (not regular password)  
→ Get it: https://myaccount.google.com/apppasswords

### No email received
→ Check spam folder  
→ Check backend logs for errors  
→ Verify you're logged in

### Button still not working
→ Check browser console (F12) for errors  
→ Make sure backend is running  
→ Try logging out and back in

---

## Quick Debug Commands

**Check if backend running:**
```bash
curl http://localhost:8000/healthz
```

**Test email directly:**
```bash
python test_email_alert.py
```

**Check backend logs:**
```bash
# Look in backend terminal for:
# "api.alerts.direct_email_sent"
# Or errors
```

---

## Backend Response Examples

### ✅ Success:
```json
{
  "success": true,
  "email_notifications_sent": true,
  "emails_sent": 1,
  "recipient": "prasathram387@gmail.com",
  "message": "✅ Response plan email sent..."
}
```

### ❌ SMTP Not Configured:
```json
{
  "success": false,
  "error": "SMTP not configured",
  "help": "Set SMTP_USER and SMTP_PASSWORD in .env"
}
```

---

## Full Documentation

- **SEND_ALERTS_BUTTON_FIX.md** - Complete technical details
- **EMAIL_SETUP_TESTING_GUIDE.md** - SMTP setup guide
- **QUICK_EMAIL_TEST.md** - Test email endpoint

---

**🎉 Your Send Alerts button is now fully functional!**

**Try it now!** It takes just 2 minutes to test.

