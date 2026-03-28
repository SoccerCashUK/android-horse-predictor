import json
import re
import requests
from collections import defaultdict

URLS = [
    "https://www.sportinglife.com/racing/abc-guide/today",
    "https://www.sportinglife.com/racing/abc-guide/tomorrow",
    "https://www.sportinglife.com/racing/abc-guide/5-days",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except: return None

def parse_html_entries(html):
    # This looks for the horse name and the race details in one big chunk
    # Pattern: Matches Horse Name followed by Time, Course, Day, and Odds
    # Example: 'Corach Rambler... 14:10 Aintree Saturday 5/1'
    entries = []
    
    # We look for anything that ends in a fraction (odds) and has a time/day before it
    raw_matches = re.findall(r"([A-Z][a-z']+(?:\s[A-Z][a-z']+)*).*?(\d{1,2}:\d{2})\s+(.+?)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)", html)
    
    for match in raw_matches:
        entries.append({
            "horse": match[0].strip(),
            "race": f"{match[1]} {match[2]}",
            "day": match[3],
            "odds": match[4]
        })
    return entries

def build_races(entries):
    races = defaultdict(list)
    for item in entries:
        dec = fractional_to_decimal(item["odds"])
        if not dec: continue
        prob = 1 / dec
        key = f'{item["day"]}_{item["race"]}'
        races[key].append({
            "horse": item["horse"],
            "odds": item["odds"],
            "decimal_odds": dec,
            "implied_prob": prob
        })

    output = []
    for key, runners in races.items():
        try:
            day, race_info = key.split("_", 1)
            time_part, course = race_info.split(" ", 1)
            total_prob = sum(r["implied_prob"] for r in runners)
            if total_prob > 0:
                for r in runners: r["implied_prob"] /= total_prob
            runners.sort(key=lambda x: x["implied_prob"], reverse=True)
            output.append({"day": day, "time": time_part, "course": course, "runners": runners})
        except: continue
    
    output.sort(key=lambda x: (x["day"], x["time"], x["course"]))
    return output

def main():
    all_entries = []
    for url in URLS:
        try:
            print(f"Fetching {url}...")
            r = requests.get(url, headers=HEADERS, timeout=30)
            entries = parse_html_entries(r.text)
            print(f"Found {len(entries)} entries")
            all_entries.extend(entries)
        except Exception as e:
            print(f"Error: {e}")

    races = build_races(all_entries)
    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(races, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(races)} races")

if __name__ == "__main__":
    main()
