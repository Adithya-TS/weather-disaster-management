# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone and Setup
```bash
cd weather-disaster-adk
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys:
# - GOOGLE_API_KEY (Gemini API)
# - OPENWEATHER_API_KEY (OpenWeatherMap)
# - Email credentials for alerts
```

### Step 3: Run Your First Check
```bash
python src/main.py --city "London"
```

Expected output:
```
{"event": "workflow.start", "workflow_id": "workflow_abc123", "city": "London"}
{"event": "agent.start", "agent": "ParallelDataCollector"}
{"event": "weather_api_tool.execute", "city": "London"}
{"event": "agent.complete", "agent": "DisasterAnalysis", "disaster_type": "..."}
...
====================================
Weather Check Complete for London
====================================
Disaster Type: No Immediate Threat
Severity: Low
Alert Sent: False
====================================
```

---

## 🧪 Run Evaluation Suite

Test the system with automated evaluation:

```bash
python src/main.py --evaluate
```

This will:
- Test disaster detection accuracy
- Evaluate response quality
- Measure performance benchmarks
- Generate `evaluation_results.json`

---

## 🔄 Continuous Monitoring

Monitor multiple cities continuously:

```bash
python src/main.py --monitor --interval 60
```

Options:
- `--interval 60` - Check every 60 seconds
- Cities defined in `.env` (CITIES=London,Karachi,Tokyo)

---

## 🐳 Docker Deployment

### Quick Deploy
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f weather-disaster-adk
```

### Stop Services
```bash
docker-compose down
```

---

##  Debug Mode

Enable detailed logging:

```bash
# In .env file:
LOG_LEVEL=DEBUG
LOG_FORMAT=console  # For readable output

# Or run with:
LOG_LEVEL=DEBUG python src/main.py --city "London"
```

---

## 📝 Common Commands

### Run Single City Check
```bash
python src/main.py --city "Tokyo"
```

### Continuous Monitoring (1 hour interval)
```bash
python src/main.py --monitor --interval 3600
```

### Evaluation with Specific Scenario
```bash
python src/main.py --evaluate
```

### Docker Build Only
```bash
docker build -t weather-disaster-adk .
```

### Docker Run Standalone
```bash
docker run -p 9090:9090 --env-file .env weather-disaster-adk
```

---

## 🆘 Troubleshooting

### Issue: Import errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key errors
```bash
# Check .env file exists and has correct keys
cat .env | grep API_KEY

# Verify environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### Issue: Docker port conflicts
```bash
# Change ports in docker-compose.yml if 9090 or 3000 are in use
ports:
  - "9092:9090"  # Changed from 9090
```

---

## 📚 Learn More

- **Full Documentation**: See `IMPLEMENTATION_GUIDE.md`
- **Code Structure**: See `README.md`
- **Implementation Details**: See `SUMMARY.md`

---

## ✅ Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file configured with API keys
- [ ] Single city check works
- [ ] Evaluation suite runs successfully
- [ ] Docker deployment (optional)

---

## 🎯 Next Steps

1. **Test different cities**: Try New York, Tokyo, Mumbai
2. **Adjust monitoring interval**: Experiment with different timings
3. **View historical data**: Check `disaster_log.json`
4. **Customize response plans**: Modify agent prompts
5. **Add more tools**: Extend `custom_tools.py`
6. **Deploy to cloud**: Use Google Cloud Run

---

**Need Help?** Check the detailed documentation in `IMPLEMENTATION_GUIDE.md`

**Ready to Deploy?** See Docker configuration in `README.md`
