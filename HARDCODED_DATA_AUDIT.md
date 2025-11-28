# Hardcoded Data Audit - Weather Disaster Management System

## Date: November 28, 2025

## Executive Summary
This audit identified **3 critical areas** where the application generates synthetic/hardcoded data instead of real data, which could potentially send misinformation to users.

---

## 🚨 CRITICAL ISSUES FOUND

### 1. **FAKE SOCIAL MEDIA REPORTS** (HIGH PRIORITY)
**File:** `src/tools/custom_tools.py`  
**Lines:** 430-531 (approximately)  
**Severity:** 🔴 CRITICAL

#### Problem:
The `get_social_media_reports()` function has a fallback that generates **completely fake social media reports** with hardcoded messages like:
- "⚠️ Rain reported in {location} - roads getting wet - @citizen1"
- "🌧️ Rainy conditions in {location}, drive carefully - @localreporter"
- And many more fake posts with fake user accounts

#### Impact:
- Users see fabricated social media posts presented as real reports
- Creates false sense of validation from "other users"
- **Direct misinformation** - violates user's requirement for accurate data only

#### Fix Applied:
✅ Modified function to ONLY return real social media data
✅ Returns clear error message if no real data available
✅ Removed all 100+ lines of synthetic report generation code

#### Code Changes:
```python
# OLD (REMOVED):
# FALLBACK: Generate synthetic reports based on actual weather data
# ... 100+ lines of fake social media posts ...

# NEW (IMPLEMENTED):
else:
    # No real reports available - return clear message instead of generating fake data
    logger.info("social_media_tool.no_data", location=location)
    return f"No real social media reports currently available for {location}. Please rely on official weather sources for accurate information."
```

---

### 2. **FAKE WEATHER FORECASTS** (HIGH PRIORITY)
**File:** `src/tools/custom_tools.py`  
**Lines:** 150-221  
**Function:** `create_climatological_forecast()`  
**Severity:** 🔴 CRITICAL

#### Problem:
For weather forecasts beyond 5 days (up to 30 days), the system generates **RANDOM/ESTIMATED data** using:
```python
random.uniform(-temp_variation, temp_variation)  # Randomized temperatures
random.uniform(-15, 15)  # Random humidity variations
random.uniform(-10, 10)  # Random pressure variations
random.uniform(0, 2)  # Random precipitation
```

#### Impact:
- Users receive fabricated forecast data presented as real predictions
- Temperature, humidity, pressure values are **randomly generated**, not from any forecast model
- Labeled as "climatological forecast" but it's just random numbers with seasonal bias

#### Recommendation:
🔧 **TO BE FIXED:**
1. Remove the `create_climatological_forecast()` function entirely
2. Limit forecasts to OpenWeatherMap's actual 5-day forecast only
3. Return error message for dates beyond 5 days: "Forecast only available for next 5 days"

#### Code to Remove/Fix:
- Lines 150-221: Delete entire `create_climatological_forecast()` function
- Lines 291-335 in `get_weather_forecast()`: Remove calls to climatological estimates
- Lines 332-335: Remove "else" branch that generates fake forecasts for days 6-30

---

### 3. **SIMULATED MCP DATA** (MEDIUM PRIORITY)
**File:** `src/tools/mcp_integration.py`  
**Lines:** 222-235  
**Function:** `_fetch_source()`  
**Severity:** 🟡 MEDIUM

#### Problem:
The MCP (Model Context Protocol) integration contains hardcoded test data:
```python
await asyncio.sleep(0.3)  # Simulate API call

# Simulate source-specific data
return {
    "source": source,
    "data": {
        "readings": [{"value": 25.5, "unit": "celsius"}],  # HARDCODED!
        "quality": "high",
        "last_update": datetime.now().isoformat()
    },
    "success": True
}
```

#### Impact:
- If this code path is used, returns fake sensor readings (always 25.5°C)
- Less critical if MCP system isn't actively used in production

#### Recommendation:
🔧 **TO BE FIXED:**
- Check if MCP integration is actually used in production
- If used: Replace with real sensor/API data sources
- If not used: Remove the entire MCP module or clearly mark as "DEMO/TEST ONLY"

---

## ✅ FIXES COMPLETED

### Social Media Reports Function
- ✅ Removed 100+ lines of hardcoded fake social media posts
- ✅ Function now returns only real data from Reddit, News APIs, RSS feeds
- ✅ Clear error messages when no real data available
- ✅ No more fabricated user accounts or fake posts

---

## 🔧 FIXES STILL NEEDED

### 1. Weather Forecast Function
**Priority:** HIGH  
**Action Required:**
```python
# In src/tools/custom_tools.py

# 1. DELETE lines 150-221 (create_climatological_forecast function)

# 2. MODIFY get_weather_forecast() function around lines 291-335:
# Remove this section:
else:
    # For days 6-30, use climatological estimates
    forecasts.append(create_climatological_forecast(...))

# Replace with:
else:
    # Only provide forecasts up to 5 days
    break  # Stop processing dates beyond 5 days

# 3. UPDATE date validation (around line 258):
if total_days > 30:
    return {
        "error": "Forecast is only available for up to 30 days..."
    }

# Change to:
if total_days > 5:
    return {
        "error": "Forecast is only available for the next 5 days from OpenWeatherMap API. For dates beyond 5 days, we cannot provide accurate forecasts.",
        "success": False
    }
```

### 2. MCP Integration
**Priority:** MEDIUM  
**Action Required:**
- Audit if MCP is used in production
- If yes: Implement real data sources
- If no: Add "DEMO ONLY" warnings or remove module

---

## 📊 SUMMARY OF HARDCODED DATA LOCATIONS

| File | Function | Lines | Issue | Status |
|------|----------|-------|-------|--------|
| `src/tools/custom_tools.py` | `get_social_media_reports()` | 430-531 | Fake social media posts | ✅ FIXED |
| `src/tools/custom_tools.py` | `create_climatological_forecast()` | 150-221 | Random weather data | ⚠️ NEEDS FIX |
| `src/tools/custom_tools.py` | `get_weather_forecast()` | 291-335 | Calls fake forecast function | ⚠️ NEEDS FIX |
| `src/tools/mcp_integration.py` | `_fetch_source()` | 222-235 | Hardcoded sensor readings | ⚠️ NEEDS REVIEW |

---

## 🎯 DATA SOURCES VERIFIED AS REAL

These components use ONLY real external APIs - NO hardcoded data:

✅ **Weather Data** (current): OpenWeatherMap API - Real-time data  
✅ **Weather Data** (0-5 days forecast): OpenWeatherMap API - Real forecast  
✅ **Geocoding**: OpenWeatherMap Geocoding API - Real location data  
✅ **Earthquake Data**: USGS API - Real seismic data  
✅ **Tsunami Warnings**: NOAA/NWS API - Real alerts  
✅ **Alert Detection**: Based on real weather thresholds, no hardcoded alerts  
✅ **Social Media** (when available): Real data from Reddit, News APIs, RSS feeds  

---

## 📝 RECOMMENDATIONS

### Immediate Actions (Before Production):
1. ✅ **DONE:** Fix social media fallback
2. ⚠️ **URGENT:** Remove fake forecast generation (days 6-30)
3. ⚠️ **URGENT:** Limit forecasts to 5 days only
4. 🔍 **REVIEW:** Audit MCP integration usage

### Code Review Checklist:
- [ ] Remove all `random.uniform()`, `random.randint()`, `random.choice()` calls from production code
- [ ] Search for keywords: "synthetic", "fake", "mock", "simulate", "hardcoded"
- [ ] Verify all API calls return real data
- [ ] Add data source attribution in UI (e.g., "Data from OpenWeatherMap API")
- [ ] Add timestamps to all data showing when it was fetched
- [ ] Implement proper error handling that doesn't fall back to fake data

### Best Practices Going Forward:
1. **Never generate synthetic data** in production code
2. **Always return errors** when real data unavailable
3. **Be transparent** about data sources and limitations
4. **Add logging** to track when real APIs are called vs. errors
5. **Test with real APIs** in staging environment

---

## 🔐 VERIFICATION

To verify all hardcoded data is removed, run:

```bash
# Search for random data generation
grep -r "random\\.uniform\|random\\.randint\|random\\.choice" src/

# Search for synthetic/fake data comments
grep -ri "synthetic\|fake\|mock\|simulate" src/ --include="*.py"

# Search for hardcoded test data
grep -r "TODO\|FIXME\|HACK" src/ --include="*.py"
```

---

## ✉️ CONTACT

For questions about this audit or implementation:
- Review Date: November 28, 2025
- Audit Focus: Hardcoded/Synthetic Data Removal
- Next Review: After fixes are applied

---

## CONCLUSION

**Current Status:** 1 out of 3 critical issues fixed  
**Remaining Work:** 2 high-priority fixes needed before production deployment  
**Risk Level:** 🟡 MEDIUM (was 🔴 HIGH before social media fix)

The application currently sends **mostly real data**, but still has fake weather forecasts for days 6-30. This must be fixed before production to ensure users receive only accurate, verifiable weather information.

