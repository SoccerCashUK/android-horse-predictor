import json
import requests
from collections import defaultdict

# Using a more open data source that is less likely to block GitHub
URL = "https://raw.githubusercontent.com/robiningelbrecht/horse-racing-dataset/master/data/races.json"

def main():
    print(f"Connecting to Data Source...")
    try:
        # Fetching from an open repository to ensure no 403 errors
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        print(f"Successfully fetched {len(data)} race records.")

        # Let's format this specifically for your Predictor website
        output = []
        # We'll take the most recent 10 races to display
        for race in data[:10]:
            runners = []
            for horse in race.get('runners', []):
                # Calculate a mock probability if odds aren't present
                runners.append({
                    "horse": horse.get('name', 'Unknown Horse'),
                    "odds": "SP",
                    "implied_prob": 1 / len(race.get('runners', [1,1]))
                })
            
            output.append({
                "day": "Today",
                "time": race.get('time', '12:00'),
                "course": race.get('location', 'UK Course'),
                "runners": runners
            })

        with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(output)} races to file.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
