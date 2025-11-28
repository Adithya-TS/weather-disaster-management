"""
Script to remove hardcoded/synthetic data from custom_tools.py
This ensures only real data is sent to users.
"""

import re

def fix_social_media_function():
    """Fix get_social_media_reports to remove synthetic fallback."""
    
    file_path = "src/tools/custom_tools.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the get_social_media_reports function and replace the fallback section
    # Pattern: from "# FALLBACK:" comment to the return statement at the end of function
    
    pattern = r'(    # Try to get real social media data first.*?return f"Social Media Reports.*?\n)(    \n    # FALLBACK: Generate synthetic reports.*?return f"Social Media Reports.*?\n)'
    
    replacement = r'\1'
    
    # Simpler approach: find and replace specific section
    old_code = """    except Exception as e:
        logger.warning("social_media_tool.real_data_failed", location=location, error=str(e))
    
    # FALLBACK: Generate synthetic reports based on actual weather data"""
    
    new_code = """    except Exception as e:
        logger.warning("social_media_tool.real_data_failed", location=location, error=str(e))
        # No fallback - return error message instead of generating fake data
        return f"Unable to fetch social media reports for {location}. Please check official weather sources for accurate information." """
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✓ Removed synthetic social media fallback trigger")
    else:
        print("✗ Could not find social media fallback section")
        return False
    
    # Now remove all the synthetic report generation code (the large block after FALLBACK comment)
    # This is everything from the try: after FALLBACK to just before the next function definition
    
    # Find the pattern for all the synthetic reports
    lines = content.split('\n')
    new_lines = []
    skip_mode = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        if '# FALLBACK: Generate synthetic reports' in line:
            skip_mode = True
            skip_count = 0
            continue
        
        if skip_mode:
            skip_count += 1
            # Look for the next function definition to know when to stop skipping
            if line.strip().startswith('def ') and skip_count > 10:
                skip_mode = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Social media function fixed - removed synthetic data generation")
    return True


def fix_weather_forecast_function():
    """Remove climatological forecast generation (random data for days 6-30)."""
    
    file_path = "src/tools/custom_tools.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the create_climatological_forecast function entirely
    pattern = r'def create_climatological_forecast\(.*?\n(?:.*?\n)*?    return \{[\s\S]*?\n    \}\n\n'
    
    matches = re.findall(pattern, content)
    if matches:
        for match in matches:
            content = content.replace(match, '')
        print("✓ Removed create_climatological_forecast() function")
    else:
        print("! Could not find create_climatological_forecast function")
    
    # Update date validation to limit to 5 days
    old_validation = """if total_days > 30:
            return {
                "error": "Forecast is only available for up to 30 days in advance. Please select a date range within 30 days.",
                "success": False
            }"""
    
    new_validation = """if total_days > 5:
            return {
                "error": "Forecast is only available for the next 5 days from OpenWeatherMap API. For longer range forecasts, the data would not be reliable.",
                "success": False
            }"""
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        print("✓ Updated forecast limit from 30 days to 5 days")
    
    # Remove calls to climatological forecast in get_weather_forecast
    old_climatology_call = """else:
                    # For days 6-30, use climatological estimates
                    forecasts.append(create_climatological_forecast(
                        date_str, current_date, baseline_temp, baseline_humidity, baseline_pressure, days_from_today
                    ))"""
    
    new_climatology_call = """else:
                    # Only provide real forecasts up to 5 days
                    logger.warning("forecast.beyond_5_days", date=date_str, location=location)
                    break  # Stop processing dates beyond OpenWeatherMap's 5-day limit"""
    
    if old_climatology_call in content:
        content = content.replace(old_climatology_call, new_climatology_call)
        print("✓ Removed climatological forecast calls from get_weather_forecast()")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Weather forecast function fixed - removed fake data generation")
    return True


def main():
    print("="*60)
    print("REMOVING HARDCODED/SYNTHETIC DATA FROM APPLICATION")
    print("="*60)
    print()
    
    print("1. Fixing Social Media Reports Function...")
    try:
        fix_social_media_function()
    except Exception as e:
        print(f"✗ Error fixing social media: {e}")
    
    print()
    print("2. Fixing Weather Forecast Function...")
    try:
        fix_weather_forecast_function()
    except Exception as e:
        print(f"✗ Error fixing weather forecast: {e}")
    
    print()
    print("="*60)
    print("FIXES COMPLETED")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Review HARDCODED_DATA_AUDIT.md for details")
    print("2. Test the application with real API calls")
    print("3. Verify no synthetic data is returned to users")
    print("4. Consider MCP integration audit (see audit document)")


if __name__ == "__main__":
    main()

