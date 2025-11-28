# Alerts & Notifications System - Setup Guide

## Overview

The Alerts & Notifications system automatically detects severe weather conditions and sends email notifications to subscribed users in affected areas.

## Features

✅ **Automatic Weather Monitoring**: Analyzes weather data for severe conditions  
✅ **Email Notifications**: Beautiful HTML emails sent to affected users  
✅ **Location-Based Subscriptions**: Users subscribe to specific locations  
✅ **Severity Filtering**: Choose which severity levels to be notified about  
✅ **Real-time Alerts**: Instant notifications when severe weather is detected  
✅ **Alert History**: View all past and active alerts  

## How It Works

### 1. Weather Analysis
The system continuously monitors weather conditions and detects:
- **Hurricane/Cyclone**: Wind speeds ≥ 118 km/h
- **Heatwave**: Temperature ≥ 40°C  
- **Flash Flood**: Precipitation ≥ 100mm
- **Heavy Rain**: Precipitation ≥ 50mm
- **Severe Storm**: High winds + heavy rain
- **Extreme Cold**: Temperature ≤ -10°C

### 2. Alert Creation
When severe conditions are detected:
1. Alert is created in the database
2. Severity level is assigned (LOW, MEDIUM, HIGH, CRITICAL)
3. System finds users subscribed to the affected location
4. Notifications are sent based on user preferences

### 3. Email Notifications
Users receive beautifully formatted emails containing:
- Alert severity and type
- Location and weather conditions
- Safety recommendations
- Timestamp and alert details

## Setup Instructions

### Step 1: Update Environment Variables

Add these variables to your `.env` file:

```bash
# Email Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # See instructions below
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Weather Disaster Management

# Optional: For development without SMTP
# Leave SMTP_USER and SMTP_PASSWORD empty to simulate email sending
```

### Step 2: Gmail App Password Setup (if using Gmail)

1. **Enable 2-Factor Authentication**:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Weather Disaster App"
   - Copy the 16-character password
   - Use this as your `SMTP_PASSWORD`

**Important**: Never commit the `.env` file with real credentials!

### Step 3: Update Database

Run the application to automatically create new database tables:

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run the FastAPI app (this will create tables automatically)
uvicorn src.api.fastapi_app:app --reload
```

New tables created:
- `alerts` - Stores weather alerts
- `user_subscriptions` - User notification preferences
- `notification_logs` - Tracks sent notifications

### Step 4: Start Frontend

```bash
cd frontend
npm run dev
```

Visit http://localhost:5173 and log in.

## Using the System

### For Users

#### 1. Subscribe to Locations

1. Navigate to **Alerts & Notifications** in the sidebar
2. Click on the **"My Subscriptions"** tab
3. Click **"Add Subscription"**
4. Enter:
   - **Location**: City name (e.g., "Chennai, India")
   - **Radius**: Alert radius in kilometers (1-500 km)
   - **Severity Levels**: Choose which alerts you want to receive
   - **Email**: Enable/disable email notifications
5. Click **"Save Subscription"**

#### 2. View Active Alerts

1. Go to **Alerts & Notifications**
2. Click on the **"Active Alerts"** tab
3. View all current severe weather alerts
4. See detailed weather conditions and safety recommendations

#### 3. Manage Subscriptions

- **Edit**: Click the pencil icon to modify settings
- **Delete**: Click the trash icon to remove subscription
- **Toggle**: Enable/disable subscriptions as needed

### For Administrators

#### Trigger Manual Weather Check

Use the API to manually check a location for severe weather:

```bash
curl -X POST "http://localhost:8000/alerts/check" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "Chennai"}'
```

#### View All Alerts

```bash
curl "http://localhost:8000/alerts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Filter by Severity

```bash
curl "http://localhost:8000/alerts/?severity=high" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## API Endpoints

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts/` | List all alerts (with filters) |
| GET | `/alerts/{alert_id}` | Get specific alert |
| POST | `/alerts/check` | Check location for severe weather |

### Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/alerts/subscriptions` | Create new subscription |
| GET | `/alerts/subscriptions` | List user's subscriptions |
| PUT | `/alerts/subscriptions/{id}` | Update subscription |
| DELETE | `/alerts/subscriptions/{id}` | Delete subscription |

## Automated Monitoring (Future Enhancement)

To enable continuous monitoring, you can set up a background task or cron job:

```python
# Add to your application
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def monitor_all_subscriptions():
    """Check weather for all active subscriptions"""
    # Get all unique locations from subscriptions
    # Check each location for severe weather
    # Create alerts and send notifications
    pass

# Schedule to run every hour
scheduler = AsyncIOScheduler()
scheduler.add_job(monitor_all_subscriptions, 'interval', hours=1)
scheduler.start()
```

## Testing

### Test Email Notifications (Development)

If SMTP is not configured, the system will log emails instead of sending them:

```python
# In logs, you'll see:
# notification_service.smtp_not_configured: SMTP not configured, simulating email send
```

### Test Alert Creation

1. Use the Disaster Response endpoint with a location known to have severe weather
2. Or manually call the `/alerts/check` endpoint
3. Check the `/alerts/` endpoint to see created alerts
4. Verify email was sent/logged

## Severity Thresholds

The system uses these thresholds to determine alert severity:

| Condition | Threshold | Severity |
|-----------|-----------|----------|
| Wind Speed | ≥ 118 km/h | CRITICAL (Hurricane) |
| Wind Speed | ≥ 70 km/h | HIGH/MEDIUM (Storm) |
| Temperature | ≥ 45°C | CRITICAL (Heatwave) |
| Temperature | ≥ 40°C | HIGH (Heatwave) |
| Temperature | ≤ -20°C | MEDIUM (Cold) |
| Temperature | ≤ -10°C | LOW (Cold) |
| Precipitation | ≥ 100mm | CRITICAL (Flood) |
| Precipitation | ≥ 50mm | HIGH (Heavy Rain) |

## Customization

### Modify Thresholds

Edit `src/services/alert_service.py`:

```python
SEVERE_THRESHOLDS = {
    "temperature_high": 40.0,  # Change this
    "wind_speed_critical": 118.0,  # Change this
    # ... etc
}
```

### Customize Email Template

Edit `src/services/notification_service.py` - methods:
- `_create_email_html()` - HTML email template
- `_create_email_text()` - Plain text template

### Add New Alert Types

1. Add to `AlertType` enum in `src/models/alert.py`
2. Add detection logic in `src/services/alert_service.py`
3. Update UI to display new type

## Troubleshooting

### Emails Not Sending

1. **Check SMTP credentials**: Verify `SMTP_USER` and `SMTP_PASSWORD` in `.env`
2. **Check Gmail settings**: Ensure 2FA is enabled and App Password is created
3. **Check logs**: Look for errors in terminal output
4. **Test SMTP connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print("SMTP connection successful!")
   ```

### Alerts Not Creating

1. **Check weather data**: Verify weather API is working
2. **Check thresholds**: Weather might not be severe enough
3. **Check logs**: Look for errors in alert service
4. **Manual test**: Use `/alerts/check` endpoint directly

### Subscriptions Not Working

1. **Check authentication**: Ensure user is logged in
2. **Check location**: Verify location can be geocoded
3. **Check database**: Ensure tables were created
4. **Check API**: Use browser DevTools to see API responses

## Database Schema

### Alerts Table
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR,  -- hurricane, flood, etc.
    severity VARCHAR,    -- low, medium, high, critical
    title VARCHAR,
    description TEXT,
    location VARCHAR,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    wind_speed FLOAT,
    precipitation FLOAT,
    humidity FLOAT,
    is_active BOOLEAN,
    is_sent BOOLEAN,
    detected_at TIMESTAMP,
    expires_at TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User Subscriptions Table
```sql
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    location VARCHAR,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    radius_km FLOAT,
    email_enabled BOOLEAN,
    phone_number VARCHAR,
    push_enabled BOOLEAN,
    notify_on_low BOOLEAN,
    notify_on_medium BOOLEAN,
    notify_on_high BOOLEAN,
    notify_on_critical BOOLEAN,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Next Steps

1. **Set up automated monitoring**: Add background tasks to check weather periodically
2. **Add SMS notifications**: Integrate Twilio or similar service
3. **Add push notifications**: Integrate Firebase Cloud Messaging
4. **Add webhook notifications**: Post to Slack, Discord, etc.
5. **Add historical data**: Show trends and past alerts
6. **Add map view**: Display alerts on an interactive map

## Support

For issues or questions:
1. Check the logs: `logs/disaster_management_*.log`
2. Check API docs: http://localhost:8000/docs
3. Review error messages in browser console

## Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit `.env` file** with real credentials
2. **Use App Passwords** for Gmail (not your regular password)
3. **Rotate credentials** regularly
4. **Use HTTPS** in production
5. **Validate user input** in location fields
6. **Rate limit** alert creation endpoints
7. **Implement email throttling** to prevent spam

---

**System Status**: ✅ Ready to use!

Navigate to **Alerts & Notifications** in your application to get started!

