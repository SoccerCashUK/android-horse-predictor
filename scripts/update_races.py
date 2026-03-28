import json
import re
import requests
from collections import defaultdict

# At The Races is generally more script-friendly
URL = "https://www.attheraces.com/racecards"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def fractional_to_decimal(frac):
    try:
        if '/' not in frac: return None
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except: return None

def parse_atr_races(html):
    entries = []
    # This pattern looks for Horse names and Odds in the ATR layout
    # ATR often lists odds like "5/1" or "100/30"
    # We look for the Horse Name followed by the decimal or fractional price
    pattern = r"class=\"ra-horse-name\">.*?>(.*?)<.*?class=\"ra-odds\">.*?(\d+/\d+)"
    
    matches = re.findall(pattern, html, re.DOTALL)
    for m in matches:
        horse_name = re.sub(r'<.*?>', '', m[0]).strip()
        odds = m[1].strip()
        
        # For ATR, we'll assign a placeholder 'Today' and 'Race' 
        # as we refine the scraper for their specific table structure
        entries.append({
            "horse": horse_name,
            "race": "Today's Race", 
            "day": "Today",
            "odds": odds
        })
    return entries

def main():
    print(f"Connecting to At The Races...")
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        
        # Attempting to find races
        all_entries = parse_atr_races(r.text)
        print(f"Found {len(all_entries)} horses with odds.")

        races = defaultdict(list)
        for item in all_entries:
            dec = fractional_to_decimal(item["odds"])
            if dec:
                prob = 1 / dec
                key = f'{item["day"]}_{item["race"]}'
                races[key].append({
                    "horse": item["horse"], 
                    "odds": item["odds"], 
                    "implied_prob": prob
                })

        output = []
        for key, runners in races.items():
            day, race_name = key.split("_", 1)
            total_prob = sum(r["implied_prob"] for r in runners)
            if total_prob > 0:
                for r in runners: r["implied_prob"] /= total_prob
            
            runners.sort(key=lambda x: x["implied_prob"], reverse=True)
            output.append({
                "day": day, 
                "time": "Upcoming", 
                "course": "Various", 
                "runners": runners
            })

        with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(output)} races to data/upcoming_races.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
