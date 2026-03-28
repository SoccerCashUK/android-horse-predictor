import json
import re
import requests
from collections import defaultdict

# Focusing on just Today to increase our chances of getting through
URLS = ["https://www.sportinglife.com/racing/abc-guide/today"]

# High-quality headers to mimic a real modern browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except: return None

def parse_html_entries(html):
    entries = []
    # This searches for the specific text pattern Sporting Life uses for horse/race data
    # It looks for: Horse Name ... Time ... Course ... Day ... Odds
    pattern = r"([A-Z]{2,}[A-Z\s']+).*?(\d{1,2}:\d{2})\s+([A-Za-z\s]+)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)"
    
    matches = re.findall(pattern, html)
    for m in matches:
        entries.append({
            "horse": m[0].strip(),
            "race": f"{m[1]} {m[2].strip()}",
            "day": m[3],
            "odds": m[4]
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
    # Create a session to keep cookies (looks more human)
    session = requests.Session()
    
    for url in URLS:
        try:
            print(f"Fetching {url}...")
            r = session.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                entries = parse_html_entries(r.text)
                print(f"Found {len(entries)} entries")
                all_entries.extend(entries)
            else:
                print(f"Blocked by website. Status code: {r.status_code}")
        except Exception as e:
            print(f"Error: {e}")

    races = build_races(all_entries)
    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(races, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(races)} races")

if __name__ == "__main__":
    main()
