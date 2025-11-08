#!/usr/bin/env python3
"""
Full funnel analysis: matches -> chats -> meetings
"""
import json
from datetime import datetime

# Load both datasets
with open('data/matches.json') as f:
    matches = json.load(f)

with open('data/conversations_features.min.json') as f:
    convos = json.load(f)

print("=" * 60)
print("YOUR COMPLETE HINGE FUNNEL")
print("=" * 60)

# Stage 1: Total Matches
total_matches = len(matches)
print(f"\n📱 STAGE 1: Total Matches")
print(f"   {total_matches:,} matches")

# Stage 2: Matches with chats
matches_with_chats = [m for m in matches if m.get('chats') and len(m['chats']) > 0]
chat_rate = len(matches_with_chats) / total_matches * 100 if total_matches > 0 else 0
print(f"\n💬 STAGE 2: Got a Response")
print(f"   {len(matches_with_chats)} matches had chats ({chat_rate:.1f}%)")
print(f"   ❌ {total_matches - len(matches_with_chats)} never responded")

# Analyze chat depths
chat_counts = [len(m['chats']) for m in matches_with_chats]
if chat_counts:
    avg_msgs = sum(chat_counts) / len(chat_counts)
    print(f"   📊 Average messages per conversation: {avg_msgs:.1f}")
    print(f"   📈 Range: {min(chat_counts)} - {max(chat_counts)} messages")

    # Distribution
    short_convos = sum(1 for c in chat_counts if c < 5)
    medium_convos = sum(1 for c in chat_counts if 5 <= c < 20)
    long_convos = sum(1 for c in chat_counts if c >= 20)
    print(f"\n   Conversation lengths:")
    print(f"   • Short (1-4 msgs): {short_convos}")
    print(f"   • Medium (5-19 msgs): {medium_convos}")
    print(f"   • Long (20+ msgs): {long_convos}")

# Stage 3: We Met tracking
matches_with_we_met = [m for m in matches if m.get('we_met') and len(m['we_met']) > 0]
tracking_rate = len(matches_with_we_met) / len(matches_with_chats) * 100 if matches_with_chats else 0
print(f"\n📝 STAGE 3: Tracked 'We Met' Status")
print(f"   {len(matches_with_we_met)} conversations tracked ({tracking_rate:.1f}% of chats)")

# Extract meeting data
all_we_met_responses = []
for match in matches_with_we_met:
    for response in match['we_met']:
        all_we_met_responses.append({
            'did_meet': response.get('did_meet_subject'),
            'was_my_type': response.get('was_my_type'),
            'timestamp': response.get('timestamp')
        })

met_yes = sum(1 for r in all_we_met_responses if r['did_meet'] == 'Yes')
met_no = sum(1 for r in all_we_met_responses if r['did_meet'] == 'No')

print(f"\n🤝 STAGE 4: Actually Met")
print(f"   {met_yes} met in person")
print(f"   {met_no} did not meet")

if met_yes > 0:
    my_type = sum(1 for r in all_we_met_responses if r['did_meet'] == 'Yes' and r.get('was_my_type') == True)
    print(f"   ❤️  {my_type} were your type ({my_type/met_yes*100:.1f}% of meetings)")

# Calculate conversion rates
print(f"\n" + "=" * 60)
print("CONVERSION FUNNEL")
print("=" * 60)
print(f"Match → Response:  {chat_rate:.1f}%")
if matches_with_chats:
    meet_rate_of_chats = met_yes / len(matches_with_chats) * 100
    print(f"Response → Meet:   {meet_rate_of_chats:.1f}%")
overall_meet_rate = met_yes / total_matches * 100 if total_matches > 0 else 0
print(f"Match → Meet:      {overall_meet_rate:.1f}%")

# Who initiated the chats?
print(f"\n" + "=" * 60)
print("MESSAGE PATTERNS")
print("=" * 60)

total_messages = sum(len(m['chats']) for m in matches if m.get('chats'))
print(f"Total messages sent/received: {total_messages:,}")

# Try to detect who sent first message based on timestamps
# (Hinge export shows messages from your side)
first_msg_analysis = []
for match in matches_with_chats:
    if match['chats']:
        first_msg_time = match['chats'][0].get('timestamp')
        match_time = match.get('match', {}).get('timestamp') if isinstance(match.get('match'), dict) else None

        if first_msg_time:
            first_msg_analysis.append({
                'first_msg': first_msg_time,
                'match_time': match_time
            })

# Summary stats
funnel_data = {
    'total_matches': total_matches,
    'matches_with_chats': len(matches_with_chats),
    'chat_rate': round(chat_rate, 1),
    'avg_messages_per_chat': round(avg_msgs, 1) if chat_counts else 0,
    'tracked_we_met': len(matches_with_we_met),
    'met_yes': met_yes,
    'met_no': met_no,
    'overall_meet_rate': round(overall_meet_rate, 2),
    'meet_rate_of_chats': round(meet_rate_of_chats, 1) if matches_with_chats else 0,
    'total_messages': total_messages,
    'conversation_distribution': {
        'short': short_convos,
        'medium': medium_convos,
        'long': long_convos
    }
}

with open('data/funnel_stats.json', 'w') as f:
    json.dump(funnel_data, f, indent=2)

print(f"\n✅ Funnel data saved to data/funnel_stats.json")
