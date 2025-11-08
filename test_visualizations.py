#!/usr/bin/env python3
"""
Test what values the visualizations will show
"""
import json
from datetime import datetime

with open('data/conversations_features.json') as f:
    data = json.load(f)

print(f"Total conversations: {len(data)}")

# Filter valid data
valid = [d for d in data if d.get('duration_hours') is not None and d['duration_hours'] >= 0]
print(f"With valid duration: {len(valid)}")

if valid:
    durations = sorted([d['duration_hours'] for d in valid])
    median_hours = durations[len(durations)//2]
    print(f"\nMedian conversation lifespan: {median_hours:.1f} hours")

# Survival rates
with_met = [d for d in data if d.get('met') in ['Yes', 'No', 'Not yet']]
print(f"\nConversations with 'met' status: {len(with_met)}")

# Invitation timing
invites = [d for d in with_met if d.get('first_invite_msg_index')]
print(f"Conversations with invites: {len(invites)}")

if invites:
    concrete = [d for d in invites if d.get('invite_is_concrete') == True]
    print(f"  Concrete invites: {len(concrete)}")
    print(f"  Non-concrete invites: {len(invites) - len(concrete)}")

# Question density & message length
quadrants = {'short-curious': 0, 'short-silent': 0, 'long-curious': 0, 'long-silent': 0}
for d in with_met:
    q_density = d.get('question_density_first10', 0)
    msg_len = d.get('median_len_first10', 0)

    if q_density is not None and msg_len is not None:
        is_curious = q_density > 0.3
        is_long = msg_len > 120

        if is_curious and not is_long:
            quadrants['short-curious'] += 1
        elif is_curious and is_long:
            quadrants['long-curious'] += 1
        elif not is_curious and is_long:
            quadrants['long-silent'] += 1
        else:
            quadrants['short-silent'] += 1

print(f"\nQuadrant distribution:")
for name, count in quadrants.items():
    print(f"  {name}: {count}")

# Check timestamps for heatmap
timestamps_available = sum(1 for d in data if d.get('first_msg_time'))
print(f"\nConversations with timestamps: {timestamps_available}")

# First message delay
with_delay = [d for d in data if d.get('first_msg_delay_minutes') is not None]
print(f"Conversations with delay data: {len(with_delay)}")
