#!/usr/bin/env python3
"""
Rebuild conversation features with complete timestamp data from matches.json
"""
import json
from datetime import datetime
import re

def parse_timestamp(ts_str):
    """Parse timestamp string to datetime"""
    if not ts_str:
        return None
    try:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None

def extract_invite_info(chats):
    """Extract first invite message index and whether it's concrete"""
    invite_keywords = ['meet', 'coffee', 'drink', 'dinner', 'lunch', 'date', 'hang', 'get together',
                      'grab', 'catch up', 'see you', 'plans', 'free', 'available', 'tomorrow', 'tonight',
                      'weekend', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    concrete_indicators = ['tonight', 'tomorrow', 'sunday', 'monday', 'tuesday', 'wednesday',
                          'thursday', 'friday', 'saturday', 'at ', 'pm', 'am', 'o\'clock',
                          'this weekend', 'next week', 'bar', 'restaurant', 'cafe']

    for idx, chat in enumerate(chats):
        body = (chat.get('body') or '').lower()

        # Check if this is an invite
        if any(keyword in body for keyword in invite_keywords):
            is_concrete = any(indicator in body for indicator in concrete_indicators)
            return idx + 1, is_concrete  # 1-indexed

    return None, None

def analyze_questions(chats, limit=10):
    """Calculate question density in first N messages"""
    first_n = chats[:limit] if len(chats) >= limit else chats
    if not first_n:
        return 0.0

    question_count = sum(1 for chat in first_n if '?' in (chat.get('body') or ''))
    return question_count / len(first_n)

def analyze_message_length(chats, limit=10):
    """Calculate median message length in first N messages"""
    first_n = chats[:limit] if len(chats) >= limit else chats
    if not first_n:
        return None

    lengths = [len(chat.get('body') or '') for chat in first_n]
    lengths.sort()
    mid = len(lengths) // 2

    if len(lengths) % 2 == 0 and len(lengths) > 0:
        return (lengths[mid-1] + lengths[mid]) / 2.0
    elif len(lengths) > 0:
        return float(lengths[mid])
    return None

# Load matches
print("Loading matches.json...")
with open('data/matches.json') as f:
    matches = json.load(f)

print(f"Processing {len(matches)} matches...")

features = []

for match in matches:
    chats = match.get('chats', [])
    we_met = match.get('we_met', [])
    match_data = match.get('match', {})

    # Skip if no chats
    if not chats:
        continue

    # Extract timestamps
    match_time = None
    if isinstance(match_data, dict):
        match_time = parse_timestamp(match_data.get('timestamp'))

    first_msg_time = parse_timestamp(chats[0].get('timestamp')) if chats else None
    last_msg_time = parse_timestamp(chats[-1].get('timestamp')) if chats else None

    # Calculate duration
    duration_hours = None
    if match_time and last_msg_time:
        duration_hours = (last_msg_time - match_time).total_seconds() / 3600
    elif first_msg_time and last_msg_time:
        duration_hours = (last_msg_time - first_msg_time).total_seconds() / 3600

    # Calculate first message delay
    first_msg_delay_minutes = None
    if match_time and first_msg_time:
        first_msg_delay_minutes = (first_msg_time - match_time).total_seconds() / 60

    # Extract invite info
    invite_index, is_concrete = extract_invite_info(chats)

    # Analyze messaging style
    question_density = analyze_questions(chats)
    median_length = analyze_message_length(chats)

    # Determine meeting status
    met = None
    if we_met:
        latest_response = we_met[-1]  # Get most recent response
        did_meet = latest_response.get('did_meet_subject')
        if did_meet == 'Yes':
            met = 'Yes'
        elif did_meet == 'No':
            met = 'No'
        else:
            met = 'Not yet'

    # Extract year
    year = None
    if first_msg_time:
        year = first_msg_time.year
    elif match_time:
        year = match_time.year

    feature_row = {
        'match_time': match_time.isoformat() if match_time else None,
        'first_msg_time': first_msg_time.isoformat() if first_msg_time else None,
        'last_msg_time': last_msg_time.isoformat() if last_msg_time else None,
        'duration_hours': round(duration_hours, 2) if duration_hours else None,
        'first_msg_delay_minutes': round(first_msg_delay_minutes, 2) if first_msg_delay_minutes else None,
        'first_invite_msg_index': float(invite_index) if invite_index else None,
        'invite_is_concrete': is_concrete,
        'question_density_first10': round(question_density, 3),
        'median_len_first10': median_length,
        'met': met,
        'year': year,
        'num_messages': len(chats)
    }

    features.append(feature_row)

print(f"\nExtracted features for {len(features)} conversations")

# Stats
with_timestamps = sum(1 for f in features if f['match_time'] or f['first_msg_time'])
with_duration = sum(1 for f in features if f['duration_hours'])
with_met = sum(1 for f in features if f['met'])
met_yes = sum(1 for f in features if f['met'] == 'Yes')

print(f"  With timestamps: {with_timestamps}")
print(f"  With duration: {with_duration}")
print(f"  With 'met' status: {with_met} (Yes: {met_yes})")

# Save
with open('data/conversations_features.json', 'w') as f:
    json.dump(features, f, indent=2)

print(f"\n✅ Saved to data/conversations_features.json")
print(f"   File size: {len(json.dumps(features)) / 1024:.1f} KB")
