# 🐛 Debug Send Alerts Button

## Step-by-Step Debugging

### 1. Open Browser Console

1. Open http://localhost:3000/response-plan
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Clear any existing logs

### 2. Click Send Alerts Button

1. Click **"Send Alerts"** button
2. Select channels (email, sms, etc.)
3. Click **"Send Alerts"** in the modal

### 3. Check Console Logs

You should see logs like this:

```
🚀 Send Alerts button clicked!
📋 Workflow data: {response_plan: "...", location: "Jaffna", ...}
📧 User email: prasathram387@gmail.com
📍 Location: Jaffna
📢 Alert channels: ["email", "sms", "push"]
📤 Sending alert payload: {response_plan: "...", channels: [...], location: "...", send_to_email: "..."}
🔄 useWorkflow.sendAlerts called with: {response_plan: "...", ...}
✅ useWorkflow.sendAlerts result: {success: true, ...}
✅ Alert response: {success: true, ...}
```

### 4. Check Network Tab

1. Go to **Network** tab in DevTools
2. Click "Send Alerts" again
3. Look for a request to `/api/v1/alerts`

**Should see:**
- **Request URL:** `http://localhost:8000/api/v1/alerts`
- **Method:** POST
- **Status:** 200 OK
- **Request Payload:** Your alert data

### 5. Common Issues & Solutions

#### Issue 1: No logs at all

**Cause:** JavaScript error before handleSendAlerts runs

**Fix:**
- Check Console for red error messages
- Check if there are syntax errors
- Make sure frontend was rebuilt/refreshed

#### Issue 2: Logs show but no network request

**Cause:** Error in sendAlerts function

**Check console for:**
- `❌ useWorkflow.sendAlerts error: ...`
- Red error messages

**Possible causes:**
- Backend not running
- CORS issue
- Network error

#### Issue 3: Network request returns error

**Check:**
- Backend terminal for errors
- Response tab in Network request
- Status code (401 = not logged in, 500 = server error)

#### Issue 4: "No response_plan" return

**Cause:** workflowData doesn't have response_plan

**Fix:**
- Make sure you ran "Analyze Disaster" first
- Check workflow data in console log
- Navigate from Home page (not direct URL)

### 6. Test Commands

**Check if backend is running:**
```bash
curl http://localhost:8000/healthz
```

**Test API directly:**
```javascript
// In browser console (while logged in):
const token = localStorage.getItem('auth_token');
const userStr = localStorage.getItem('auth_user');
const user = JSON.parse(userStr);

fetch('http://localhost:8000/api/v1/alerts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    response_plan: 'Test plan',
    channels: ['email'],
    location: 'Test',
    send_to_email: user.email
  })
})
.then(r => r.json())
.then(data => console.log('API Response:', data))
.catch(err => console.error('API Error:', err));
```

### 7. Expected API Response

**Success:**
```json
{
  "success": true,
  "email_notifications_sent": true,
  "emails_sent": 1,
  "recipient": "prasathram387@gmail.com",
  "message": "✅ Response plan email sent to prasathram387@gmail.com",
  "timestamp": "2025-11-28T..."
}
```

**SMTP Not Configured:**
```json
{
  "success": false,
  "error": "SMTP not configured",
  "message": "⚠️ Email cannot be sent - SMTP credentials not set"
}
```

### 8. Full Debug Checklist

- [ ] Frontend is running (localhost:3000)
- [ ] Backend is running (localhost:8000)
- [ ] Logged in with Google
- [ ] Ran disaster analysis first
- [ ] On /response-plan page
- [ ] Browser console open
- [ ] Network tab open
- [ ] Clicked Send Alerts button
- [ ] Logs appear in console
- [ ] Network request appears
- [ ] Response is 200 OK

### 9. Quick Fixes

**If button does nothing:**
```bash
# Restart frontend
cd frontend
npm run dev
```

**If API returns 401:**
```javascript
// Check if logged in
console.log('Token:', localStorage.getItem('auth_token'));
console.log('User:', localStorage.getItem('auth_user'));
```

**If API returns 500:**
```bash
# Check backend logs
# Should see error messages in backend terminal
```

### 10. Manual Test

If automated doesn't work, test manually:

```javascript
// Copy-paste into browser console:
(async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('auth_user');
    
    if (!token || !userStr) {
      console.error('❌ Not logged in!');
      return;
    }
    
    const user = JSON.parse(userStr);
    console.log('✅ Logged in as:', user.email);
    
    const response = await fetch('http://localhost:8000/api/v1/alerts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        response_plan: 'This is a test emergency response plan for Jaffna.',
        channels: ['email', 'sms'],
        location: 'Jaffna, Northern Province, Sri Lanka',
        send_to_email: user.email
      })
    });
    
    const data = await response.json();
    console.log('📬 API Response:', data);
    
    if (data.success && data.email_notifications_sent) {
      console.log('✅ Email sent! Check inbox:', user.email);
    } else {
      console.log('⚠️ Response:', data);
    }
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

---

## Still Not Working?

### Check These:

1. **Backend Terminal:**
   - Look for `api.alerts.direct_email_sent` or errors
   - Check for SMTP authentication errors

2. **Frontend Terminal:**
   - Look for build errors
   - Make sure Vite is running

3. **Browser Console:**
   - Red error messages?
   - CORS errors?
   - Network errors?

4. **Network Tab:**
   - Request sent?
   - What status code?
   - What response body?

### Get Full Stack Trace:

```javascript
// In browser console:
window.addEventListener('error', (e) => {
  console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled promise rejection:', e.reason);
});
```

---

**With these debug logs, you should be able to see exactly where the problem is!**

Let me know what you see in the console when you click the button.

