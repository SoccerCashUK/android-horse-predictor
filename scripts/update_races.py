import json
import re
import requests
from collections import defaultdict
from bs4 import BeautifulSoup

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

def parse_sporting_life(html):
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    
    # Look for the race cards on the ABC guide
    sections = soup.find_all('div', class_=re.compile('ABCGuideHorse__Container'))
    
    for section in sections:
        try:
            horse_name = section.find('span', class_=re.compile('HorseName')).text.strip()
            race_info = section.find('div', class_=re.compile('RaceInfo')).text.strip()
            # Pattern: 14:10 Kempton Park Monday 5/1
            match = re.search(r"(\d{1,2}:\d{2})\s+(.+?)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)", race_info)
            
            if match:
                entries.append({
                    "horse": horse_name,
                    "race": f"{match.group(1)} {match.group(2)}",
                    "day": match.group(3),
                    "odds": match.group(4)
                })
        except:
            continue
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
        day, race_name = key.split("_", 1)
        time_part, course = race_name.split(" ", 1)
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
            entries = parse_sporting_life(r.text)
            print(f"Found {len(entries)} entries")
            all_entries.extend(entries)
        except Exception as e:
            print(f"Error: {e}")

    races = build_races(all_entries)
    with open("data/upcoming_races.json", "w") as f:
        json.dump(races, f, indent=2)
    print(f"Wrote {len(races)} races")

if __name__ == "__main__":
    main()
