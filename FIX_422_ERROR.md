# Fix for 422 Error - Alerts & Notifications

## Problem
The `/alerts/subscriptions` endpoint was returning a 422 error due to Pydantic v1 vs v2 compatibility issue.

## What Was Fixed
Changed all occurrences of `SubscriptionResponse.from_orm()` to `SubscriptionResponse.model_validate()` in `src/routes/alert_routes.py`.

**Pydantic v1 (old):**
```python
return SubscriptionResponse.from_orm(subscription)
```

**Pydantic v2 (new):**
```python
return SubscriptionResponse.model_validate(subscription)
```

## How to Apply the Fix

### Step 1: Stop the Backend Server

In the terminal where the backend is running:
1. Press `Ctrl + C` to stop uvicorn
2. Wait for it to shut down completely

### Step 2: Restart the Backend Server

```bash
# Make sure you're in the project root directory
cd C:\Users\ramprasath.t\Documents\weather-disaster-management

# Activate virtual environment (if not already active)
.\venv\Scripts\activate

# Start the server
uvicorn src.api.fastapi_app:app --reload
```

### Step 3: Verify the Fix

1. Wait for the server to start (you should see "Application startup complete")
2. Refresh your browser at http://localhost:3000
3. Navigate to **Alerts & Notifications**
4. The "My Subscriptions" tab should now load without errors

## Expected Behavior

After restarting, you should see:
- ✅ No 422 errors
- ✅ Subscriptions tab loads successfully
- ✅ Can create new subscriptions
- ✅ Can view, edit, and delete subscriptions

## If You Still See Errors

1. **Check terminal for errors**: Look at the uvicorn output for any error messages
2. **Check browser console**: Open DevTools (F12) and check for new errors
3. **Verify database connection**: Make sure PostgreSQL is running on port 5432
4. **Clear browser cache**: Try hard refresh (Ctrl + Shift + R)

## Testing the Fix

Once the server restarts, test the endpoints:

```bash
# Get subscriptions (should return empty array or your subscriptions)
curl "http://localhost:8000/alerts/subscriptions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Should return: []
# or [{"id": 1, "location": "Chennai", ...}]
```

## Files Changed

- `src/routes/alert_routes.py` - Fixed Pydantic serialization (3 locations)

## Why This Happened

The code was written using Pydantic v1 syntax (`from_orm()`), but your project uses Pydantic v2, which renamed this method to `model_validate()`.

**Pydantic v2 Migration Changes:**
- `from_orm()` → `model_validate()`
- `orm_mode = True` → `from_attributes = True` (already correct in our code)

---

**Status**: ✅ Fix Applied - Restart backend to apply changes

