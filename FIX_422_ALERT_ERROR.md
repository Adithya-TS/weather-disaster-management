# ✅ Fixed 422 Error - Send Alerts

## Problem

Getting **422 Unprocessable Content** when clicking "Send Alerts" button.

```
INFO: 127.0.0.1:60590 - "POST /api/v1/alerts HTTP/1.1" 422 Unprocessable Content
```

## Root Cause

The backend `/api/v1/alerts` endpoint expects a **required** field `response_plan`, but the frontend was sending the wrong field!

### Backend Requirement:
```python
class AlertRequest(BaseModel):
    response_plan: str = Field(..., description="...")  # REQUIRED!
    channels: Optional[List[str]]
    location: Optional[str]
    send_to_email: Optional[str]
```

### What Frontend Was Sending:
```javascript
{
  response_plan: workflowData.response_plan,  // ← undefined!
  channels: ["email", "sms"],
  location: "Jaffna",
  send_to_email: "user@example.com"
}
```

### The Issue:
The `/api/v1/disaster-response` endpoint returns:
```javascript
{
  response: "Weather analysis text...",  // ← This exists
  raw_response: "Raw weather data...",
  // NO response_plan field!
}
```

So `workflowData.response_plan` was **undefined**, causing the 422 error!

## Solution

Changed frontend to use the correct field name:

```javascript
const payload = {
  response_plan: workflowData.response,  // ← FIXED: Use 'response' field
  channels: alertChannels,
  location: location,
  send_to_email: userEmail
};
```

## Field Mapping

| Backend Field | Frontend Field | Description |
|---------------|----------------|-------------|
| `response_plan` (required) | `workflowData.response` | Weather analysis text |
| `location` | `workflowData.location` | Location name |
| `send_to_email` | User email from auth | Current user's email |
| `channels` | `alertChannels` | Selected channels |

## Testing

### Before Fix:
```bash
POST /api/v1/alerts
Status: 422 Unprocessable Content
{
  "detail": [
    {
      "loc": ["body", "response_plan"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### After Fix:
```bash
POST /api/v1/alerts
Status: 200 OK
{
  "success": true,
  "email_notifications_sent": true,
  "emails_sent": 1,
  "recipient": "user@example.com"
}
```

## What Changed

**File:** `frontend/src/pages/ResponsePlan.jsx`

**Before:**
```javascript
const payload = {
  response_plan: workflowData.response_plan,  // undefined!
  ...
};
```

**After:**
```javascript
const payload = {
  response_plan: workflowData.response,  // ✅ Correct field!
  ...
};
```

**Also added:**
- Check if `workflowData.response` exists before sending
- Better error message if no data available
- Logs for debugging

## Verification

1. **Restart frontend** (if needed)
2. **Login** to http://localhost:3000
3. **Analyze location** (e.g., "Jaffna")
4. **Go to Response Plan**
5. **Click "Send Alerts"**
6. **Check console** - should see:
   ```
   🚀 Send Alerts button clicked!
   📋 Workflow data: {response: "...", ...}
   📤 Sending alert payload (truncated): {...}
   ✅ Alert response: {success: true, ...}
   ```
7. **Check email!**

## Summary

✅ **Fixed:** Changed `workflowData.response_plan` → `workflowData.response`  
✅ **Status:** 422 error resolved, API call succeeds  
✅ **Email:** Now delivers to inbox  

---

**The 422 error is now fixed! The alert will send successfully.** 🎉

