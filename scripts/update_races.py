import json
import requests
import os
from datetime import datetime

# We pull these from the "Vault" we just set up
API_USER = os.getenv("RACING_API_USER")
API_PASS = os.getenv("RACING_API_PASS")

def main():
    print("Connecting to TheRacingAPI.com...")
    
    if not API_USER or not API_PASS:
        print("❌ Error: API credentials missing from GitHub Secrets!")
        return

    try:
        # 1. Authenticate and get data
        # Note: TheRacingAPI often uses Basic Auth or a simple API Key. 
        # Using the standard endpoint:
        url = "https://api.theracingapi.com/v1/racecards/free"
        
        response = requests.get(url, auth=(API_USER, API_PASS), timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            racecards = data.get('racecards', [])
            
            output = []
            for race in racecards:
                runners = []
                for horse in race.get('runners', []):
                    runners.append({
                        "horse": horse.get('name'),
                        "odds": horse.get('odds', 'SP'),
                        "implied_prob": 1.0 / len(race.get('runners', [1]))
                    })
                
                output.append({
                    "day": "Today",
                    "time": race.get('time'),
                    "course": race.get('course'),
                    "runners": runners
                })

            with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"✅ Success! Loaded {len(output)} races.")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ System Error: {e}")

if __name__ == "__main__":
    main()
