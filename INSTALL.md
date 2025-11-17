# Installation Requirements

## Install Google ADK

```bash
pip install google-adk
```

This will install:
- `google-adk` - The Agent Development Kit
- `google-genai` - Gemini AI SDK
- All required dependencies

## Verify Installation

```bash
python -c "import google.adk; print('ADK installed successfully')"
```

## Full Requirements

Your `requirements.txt` already contains most dependencies. Add:

```txt
google-adk>=0.1.0
```

## Install All Requirements

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```bash
# Required for Gemini LLM
GOOGLE_API_KEY=your-gemini-api-key-here

# Required for weather data
OPENWEATHER_API_KEY=your-openweather-api-key-here

# Optional
LOG_LEVEL=INFO
LOG_FORMAT=json
DEMO_CITY=Miami
```

## Get API Keys

1. **Google API Key**: https://aistudio.google.com/app/apikey
2. **OpenWeather API Key**: https://openweathermap.org/api

## Test Installation

```bash
# Run tests (doesn't need API keys for most tests)
python test_adk_implementation.py

# Run full system (needs API keys)
python src/main.py
```
