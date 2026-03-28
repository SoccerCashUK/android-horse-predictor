import json
import re
import requests
from collections import defaultdict

URLS = [
    "https://www.sportinglife.com/racing/abc-guide/today",
    "https://www.sportinglife.com/racing/abc-guide/tomorrow",
    "https://www.sportinglife.com/racing/abc-guide/5-days",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except: return None

def parse_html_entries(html):
    # Remove HTML tags to get clean text
    text = re.sub(r"<[^>]+>", "\n", html)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    entries = []
    # This pattern looks for: 14:10 Kempton Monday 5/1
    pattern = r"(\d{1,2}:\d{2})\s+(.+?)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)"
    
    for i in range(len(lines)):
        match = re.search(pattern, lines[i])
        if match:
            # The horse name is usually the line right BEFORE the race info
            horse_name = lines[i-1] if i > 0 else "Unknown Horse"
            
            entries.append({
                "horse": horse_name,
                "race": f"{match.group(1)} {match.group(2)}",
                "day": match.group(3),
                "odds": match.group(4)
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
        parts = key.split("_", 1)
        day = parts[0]
        race_info = parts[1].split(" ", 1)
        time_part = race_info[0]
        course = race_info[1]
        
        total_prob = sum(r["implied_prob"] for r in runners)
        if total_prob > 0:
            for r in runners: r["implied_prob"] /= total_prob
        
        runners.sort(key=lambda x: x["implied_prob"], reverse=True)
        output.append({"day": day, "time": time_part, "course": course, "runners": runners})
    
    output.sort(key=lambda x: (x["day"], x["time"], x["course"]))
    return output

def main():
    all_entries = []
    for url in URLS:
        try:
            print(f"Fetching {url}...")
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
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
