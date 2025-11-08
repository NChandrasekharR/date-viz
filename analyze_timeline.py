#!/usr/bin/env python3
"""
Analyze timeline of Hinge activity
"""
import json
from datetime import datetime
from collections import Counter

# Load matches
with open('data/matches.json') as f:
    matches = json.load(f)

# Extract all chat timestamps
all_timestamps = []
for match in matches:
    if 'chats' in match and match['chats']:
        for chat in match['chats']:
            if 'timestamp' in chat and chat['timestamp']:
                try:
                    ts = datetime.strptime(chat['timestamp'], '%Y-%m-%d %H:%M:%S')
                    all_timestamps.append(ts)
                except:
                    pass

print(f"📅 Total messages: {len(all_timestamps)}")

if all_timestamps:
    all_timestamps.sort()
    earliest = all_timestamps[0]
    latest = all_timestamps[-1]

    print(f"📆 Active from: {earliest.strftime('%B %Y')} to {latest.strftime('%B %Y')}")
    print(f"⏱️  Duration: {(latest - earliest).days} days")

    # Group by month
    by_month = Counter(ts.strftime('%Y-%m') for ts in all_timestamps)

    print(f"\n📊 Monthly Activity (top 10 months):")
    for month, count in by_month.most_common(10):
        bar = '█' * (count // 20)
        print(f"  {month}: {count:4d} {bar}")

    # Group by year
    by_year = Counter(ts.year for ts in all_timestamps)
    print(f"\n📅 By Year:")
    for year in sorted(by_year.keys()):
        count = by_year[year]
        bar = '█' * (count // 100)
        print(f"  {year}: {count:4d} {bar}")

    # Day of week analysis
    by_dow = Counter(ts.strftime('%A') for ts in all_timestamps)
    days_ordered = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    print(f"\n📊 Activity by Day of Week:")
    for day in days_ordered:
        count = by_dow.get(day, 0)
        bar = '█' * (count // 50)
        print(f"  {day:9s}: {count:4d} {bar}")

    # Hour of day analysis
    by_hour = Counter(ts.hour for ts in all_timestamps)

    print(f"\n🕐 Most Active Hours:")
    for hour in sorted(by_hour.keys(), key=lambda h: by_hour[h], reverse=True)[:5]:
        count = by_hour[hour]
        time_str = f"{hour:02d}:00-{hour+1:02d}:00"
        print(f"  {time_str}: {count:4d} messages")

    # Save timeline data for viz
    timeline_data = {
        'earliest': earliest.isoformat(),
        'latest': latest.isoformat(),
        'total_messages': len(all_timestamps),
        'duration_days': (latest - earliest).days,
        'by_month': [{'month': k, 'count': v} for k, v in sorted(by_month.items())],
        'by_year': {str(k): v for k, v in by_year.items()},
        'by_day_of_week': dict(by_dow),
        'by_hour': {str(k): v for k, v in by_hour.items()}
    }

    with open('data/timeline_stats.json', 'w') as f:
        json.dump(timeline_data, f, indent=2)

    print(f"\n✅ Timeline data saved to data/timeline_stats.json")
