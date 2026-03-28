import json
import datetime

def main():
    print("Generating internal test data...")
    
    # We create our own data so no website can block us
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    output = [{
        "day": "Test Day",
        "time": current_time,
        "course": "Local Test Track",
        "runners": [
            {"horse": "Connection Success", "odds": "1/1", "implied_prob": 0.5},
            {"horse": "Script Working", "odds": "1/1", "implied_prob": 0.5}
        ]
    }]

    try:
        with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"✅ SUCCESS: Internal data written at {current_time}")
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    main()
