import json
import requests
import os
from datetime import datetime

API_USER = os.getenv("RACING_API_USER")
API_PASS = os.getenv("RACING_API_PASS")

def main():
    print("Connecting to TheRacingAPI.com...")
    if not API_USER or not API_PASS:
        print("❌ Error: API credentials missing!")
        return

    try:
        # Requesting the racecards
        url = "https://api.theracingapi.com/v1/racecards/free"
        response = requests.get(url, auth=(API_USER, API_PASS), timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a list called 'racecards'
            racecards = data.get('racecards', [])
            
            formatted_output = []
            for race in racecards:
                runners = []
                # TheRacingAPI uses 'runners' list inside each race
                for horse in race.get('runners', []):
                    runners.append({
                        "horse": horse.get('horse_name', 'Unknown'), # API uses horse_name
                        "odds": horse.get('traditional_odds', 'SP'), # API uses traditional_odds
                        "implied_prob": 10.0 # Placeholder for your prediction logic
                    })
                
                formatted_output.append({
                    "day": "Today",
                    "time": race.get('race_time', 'N/A'), # API uses race_time
                    "course": race.get('course', 'Unknown'),
                    "runners": runners
                })

            # Save the file
            os.makedirs("data", exist_ok=True)
            with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
                json.dump(formatted_output, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Success! Correctly formatted {len(formatted_output)} races.")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Script Error: {e}")

if __name__ == "__main__":
    main()
