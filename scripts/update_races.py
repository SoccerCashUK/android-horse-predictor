import json
import re
import requests
from collections import defaultdict

# Only trying Today to minimize the footprint
URL = "https://www.sportinglife.com/racing/abc-guide/today"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except: return None

def parse_html_entries(html):
    entries = []
    # Very loose pattern: Word Word ... Time ... Course ... Day ... Odds
    pattern = r"([A-Z][a-z']+(?:\s[A-Z][a-z']+)*).*?(\d{1,2}:\d{2})\s+([A-Za-z\s]+)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)"
    
    matches = re.findall(pattern, html)
    for m in matches:
        entries.append({
            "horse": m[0].strip(),
            "race": f"{m[1]} {m[2].strip()}",
            "day": m[3],
            "odds": m[4]
        })
    return entries

def main():
    all_entries = []
    print(f"Connecting to {URL}...")
    try:
        # Added a strict 10 second timeout so it doesn't hang
        r = requests.get(URL, headers=HEADERS, timeout=10)
        
        if r.status_code == 200:
            print("Successfully reached the site.")
            all_entries = parse_html_entries(r.text)
            print(f"Found {len(all_entries)} entries")
        else:
            print(f"Access Denied (Code: {r.status_code})")
            
    except requests.exceptions.Timeout:
        print("The website took too long to respond. They are likely blocking us.")
    except Exception as e:
        print(f"Error: {e}")

    # Process and save
    races = defaultdict(list)
    for item in all_entries:
        dec = fractional_to_decimal(item["odds"])
        if dec:
            prob = 1 / dec
            key = f'{item["day"]}_{item["race"]}'
            races[key].append({"horse": item["horse"], "odds": item["odds"], "implied_prob": prob})

    output = []
    for key, runners in races.items():
        day, race_info = key.split("_", 1)
        time_part, course = race_info.split(" ", 1)
        total_prob = sum(r["implied_prob"] for r in runners)
        if total_prob > 0:
            for r in runners: r["implied_prob"] /= total_prob
        runners.sort(key=lambda x: x["implied_prob"], reverse=True)
        output.append({"day": day, "time": time_part, "course": course, "runners": runners})

    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(output)} races to file.")

if __name__ == "__main__":
    main()
