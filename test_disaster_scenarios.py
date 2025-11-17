"""
Test Disaster Management System with Different Scenarios
Run: python test_disaster_scenarios.py
"""

import asyncio
from src.main import WorkflowExecutor


async def test_disaster_scenarios():
    """Test different disaster scenarios across multiple cities."""
    
    # Define test scenarios
    scenarios = [
        {
            "city": "Miami",
            "description": "Hurricane-prone coastal city"
        },
        {
            "city": "Los Angeles", 
            "description": "Earthquake and wildfire risk"
        },
        {
            "city": "New Orleans",
            "description": "Flooding and storm surge"
        },
        {
            "city": "Houston",
            "description": "Hurricane and flooding"
        },
        {
            "city": "Phoenix",
            "description": "Extreme heat and dust storms"
        }
    ]
    
    print("\n" + "="*70)
    print("DISASTER MANAGEMENT SYSTEM - MULTI-SCENARIO TEST")
    print("="*70 + "\n")
    
    # Create executor once
    executor = WorkflowExecutor()
    
    results = []
    
    # Test each scenario
    for idx, scenario in enumerate(scenarios, 1):
        city = scenario["city"]
        description = scenario["description"]
        
        print(f"\n{'─'*70}")
        print(f"SCENARIO {idx}/{len(scenarios)}: {city}")
        print(f"Risk Profile: {description}")
        print(f"{'─'*70}\n")
        
        try:
            result = await executor.execute(city)
            results.append({
                "scenario": idx,
                "city": city,
                "success": result["success"],
                "duration": result.get("duration", 0),
                "response": result.get("response", "")[:200] + "..."  # First 200 chars
            })
            
            if result["success"]:
                print(f"✅ SUCCESS - Duration: {result['duration']:.2f}s")
                print(f"\nResponse Preview:\n{result['response'][:300]}...")
            else:
                print(f"❌ FAILED - {result.get('error')}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "scenario": idx,
                "city": city,
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nResults: {successful}/{total} scenarios completed successfully")
    print(f"Success Rate: {(successful/total)*100:.1f}%\n")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        city = result["city"]
        duration = result.get("duration", 0)
        print(f"{status} Scenario {result['scenario']}: {city:15s} - {duration:.2f}s")
    
    print("\n" + "="*70 + "\n")


async def test_single_city(city: str):
    """Test a single city scenario."""
    print(f"\n{'='*70}")
    print(f"TESTING DISASTER MANAGEMENT FOR: {city.upper()}")
    print(f"{'='*70}\n")
    
    executor = WorkflowExecutor()
    result = await executor.execute(city)
    
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Success: {result['success']}")
    print(f"City: {result['city']}")
    
    if result['success']:
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"\n{'-'*70}")
        print("FULL AGENT RESPONSE:")
        print(f"{'-'*70}\n")
        print(result['response'])
    else:
        print(f"Error: {result.get('error')}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test single city from command line
        city = " ".join(sys.argv[1:])
        asyncio.run(test_single_city(city))
    else:
        # Run all scenarios
        asyncio.run(test_disaster_scenarios())
