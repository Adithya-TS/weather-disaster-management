# API Request Examples

## POST /api/v1/alerts

### Example Request Body:
```json
{
  "response_plan": "EMERGENCY RESPONSE PLAN - MIAMI\n============================================================\nDisaster Type: Hurricane\nSeverity Level: Critical\nGenerated: 2024-01-15 14:30:00\n\nIMMEDIATE ACTIONS:\n1. IMMEDIATE: Activate Emergency Operations Center\n2. IMMEDIATE: Deploy all first responders\n3. IMMEDIATE: Issue mandatory evacuation orders\n4. IMMEDIATE: Request state/federal assistance\n\nRESOURCES TO DEPLOY:\n- Emergency Medical Services\n- Fire and Rescue Teams\n- Police Department\n- Public Works Department\n\nTIMELINE: Execute within 15 minutes\n============================================================",
  "channels": [
    "Emergency Alert System (EAS)",
    "Wireless Emergency Alerts (WEA)",
    "Email Distribution",
    "SMS Text Messages",
    "Social Media",
    "Local News Media"
  ]
}
```

### Minimal Example (uses default channels):
```json
{
  "response_plan": "EMERGENCY: Hurricane approaching Miami. Evacuate immediately. Seek shelter in designated safe zones."
}
```

### Example with Custom Channels:
```json
{
  "response_plan": "Severe weather alert: High winds and flooding expected in Miami area. Stay indoors and avoid travel.",
  "channels": [
    "SMS Text Messages",
    "Email Distribution",
    "Push Notifications"
  ]
}
```

## POST /api/v1/plan

### Example Request Body:
```json
{
  "disaster_type": "Hurricane",
  "severity": "Critical",
  "city": "Miami"
}
```

## POST /api/v1/analyze

### Example Request Body:
```json
{
  "city": "Miami"
}
```

### With Pre-fetched Data:
```json
{
  "city": "Miami",
  "weather_data": "Weather Data for Miami:\n- Conditions: heavy rain\n- Temperature: 28.5°C\n- Wind Speed: 45.0 m/s\n- Humidity: 95%\n- Pressure: 950 hPa\n- Cloud Cover: 100%",
  "social_reports": "Social Media Reports for Miami:\n⚠️ Hurricane reported in Miami - stay safe - @citizen1\n🌩️ Lightning seen in Miami skies - @localreporter"
}
```

## POST /api/v1/verify

### Example Request Body:
```json
{
  "response_plan": "EMERGENCY RESPONSE PLAN - MIAMI\n============================================================\nDisaster Type: Hurricane\nSeverity Level: Critical\n\nIMMEDIATE ACTIONS:\n1. IMMEDIATE: Activate Emergency Operations Center\n2. IMMEDIATE: Deploy all first responders\n3. IMMEDIATE: Issue mandatory evacuation orders\n\nTIMELINE: Execute within 15 minutes\n============================================================"
}
```

## POST /api/v1/disaster-response

### Example Request Body:
```json
{
  "city": "Miami"
}
```

