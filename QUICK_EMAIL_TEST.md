# 🚀 Quick Email Test - 3 Steps!

## ⚡ Fast Track (5 Minutes)

### Step 1: Setup Gmail App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. Create app password for "Mail"
3. Copy the 16-character password

### Step 2: Update `.env` File

Add these lines to your `.env` file:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=paste-16-char-app-password-here
FROM_EMAIL=your.email@gmail.com
```

**Save the file!**

### Step 3: Restart Backend & Test

```bash
# In backend terminal, press Ctrl+C, then:
uvicorn src.api.fastapi_app:app --reload
```

**Wait for:** `Application startup complete.`

### Step 4: Run Test Script

```bash
python test_email_alert.py
```

Follow the prompts to send a test email to yourself!

---

## 📱 Alternative: Test via Web Browser

1. **Login** to http://localhost:3000
2. **Open Console** (Press F12)
3. **Run this command:**

```javascript
// Get your token
const token = localStorage.getItem('token');

// Send test email
fetch('http://localhost:8000/alerts/test-email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    email: 'YOUR_EMAIL@gmail.com',  // Change this!
    location: 'Test Location'
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Result:', data);
  if (data.success) {
    alert('✅ Test email sent! Check your inbox.');
  } else {
    alert('❌ Failed: ' + data.error);
  }
});
```

---

## ✅ What You Should See

**Success Response:**
```json
{
  "success": true,
  "message": "Test email sent successfully to your.email@gmail.com",
  "details": "Check your inbox (and spam folder)"
}
```

**Then check your email!** You should receive a beautiful weather alert email.

---

## ❌ Common Errors & Fixes

### Error: "SMTP not configured"

**Fix:** Add SMTP credentials to `.env` file (Step 2 above)

### Error: "SMTP Authentication Failed"

**Fix:** 
- You're using regular password instead of App Password
- Get Gmail App Password: https://myaccount.google.com/apppasswords
- Use the 16-character password (no spaces)

### Error: "Backend is NOT running"

**Fix:** Start backend:
```bash
uvicorn src.api.fastapi_app:app --reload
```

### Error: "Unauthorized" or "User not found"

**Fix:** 
- Login to web UI: http://localhost:3000
- Make sure you're logged in before testing

---

## 📧 What's in the Test Email?

The test email includes:
- ⚠️ Alert header with severity color
- 📍 Location: "Test Location"
- 🌡️ Weather data (sample):
  - Temperature: 25.0°C
  - Wind Speed: 45.0 km/h  
  - Precipitation: 10.5 mm
  - Humidity: 80.0%
- 🛡️ Safety recommendations
- 💼 Professional HTML design

---

## 🎯 After Email Works

### 1. Create Subscription

Users can subscribe to get alerts for real locations:

```bash
POST /alerts/subscriptions
{
  "location": "Jaffna",
  "email_enabled": true,
  "notify_on_high": true,
  "notify_on_critical": true
}
```

### 2. Automatic Alerts

When you analyze a location with severe weather:

```bash
POST /api/v1/disaster-response
{
  "location": "Jaffna"
}
```

If severe conditions detected:
- ✅ Alert created
- ✅ Emails sent to subscribers
- ✅ Notifications logged

---

## 📚 Full Documentation

- **EMAIL_SETUP_TESTING_GUIDE.md** - Complete email setup guide
- **ALERTS_SETUP_GUIDE.md** - Alert system overview
- **ALERTS_IMPLEMENTATION_SUMMARY.md** - Technical details

---

## 🆘 Need Help?

1. Check backend logs for errors
2. Verify `.env` file is saved
3. Make sure backend restarted after changing `.env`
4. Try running `python test_email_alert.py` - it shows helpful error messages

---

**🎉 That's it! Email alerts are now ready to use!**

