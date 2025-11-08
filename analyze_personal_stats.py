#!/usr/bin/env python3
"""
Quick analysis script to compute personal Hinge statistics
"""
import json
from pathlib import Path

# Load data
data_path = Path(__file__).parent / 'data' / 'conversations_features.min.json'
with open(data_path) as f:
    data = json.load(f)

# Filter valid entries
valid_data = [d for d in data if d.get('met') in ['Yes', 'No', 'Not yet']]

# Total conversations
total_convos = len(valid_data)
print(f"📊 Total Conversations: {total_convos}")

# Meeting stats
met_yes = [d for d in valid_data if d.get('met') == 'Yes']
met_no = [d for d in valid_data if d.get('met') == 'No']
met_not_yet = [d for d in valid_data if d.get('met') == 'Not yet']

meet_count = len(met_yes)
meet_rate = (meet_count / total_convos * 100) if total_convos > 0 else 0
print(f"🤝 Met in Person: {meet_count} ({meet_rate:.1f}%)")
print(f"❌ Did Not Meet: {len(met_no)}")
print(f"⏳ Not Yet: {len(met_not_yet)}")

# Concrete vs non-concrete invites
concrete_invites = [d for d in met_yes if d.get('invite_is_concrete') == True]
non_concrete_invites = [d for d in met_yes if d.get('invite_is_concrete') == False]

print(f"\n📅 Concrete Invites → Met: {len(concrete_invites)}")
print(f"💬 Non-Concrete Invites → Met: {len(non_concrete_invites)}")

# Best invite timing (among successful meetings)
invite_indices = [d.get('first_invite_msg_index') for d in met_yes if d.get('first_invite_msg_index') is not None]
if invite_indices:
    avg_invite_index = sum(invite_indices) / len(invite_indices)
    print(f"\n⏱️  Average First Invite Message #: {avg_invite_index:.1f}")

    # Most common range
    early_invites = sum(1 for i in invite_indices if i <= 3)
    mid_invites = sum(1 for i in invite_indices if 4 <= i <= 10)
    late_invites = sum(1 for i in invite_indices if i > 10)
    print(f"   Early (1-3): {early_invites}, Mid (4-10): {mid_invites}, Late (11+): {late_invites}")

# Question density for successful meetings
question_densities = [d.get('question_density_first10') for d in met_yes if d.get('question_density_first10') is not None]
if question_densities:
    avg_q_density = sum(question_densities) / len(question_densities)
    print(f"\n❓ Your Avg Question Density (met): {avg_q_density:.2f}")

# Message length for successful meetings
msg_lengths = [d.get('median_len_first10') for d in met_yes if d.get('median_len_first10') is not None]
if msg_lengths:
    avg_msg_len = sum(msg_lengths) / len(msg_lengths)
    print(f"📝 Your Avg Message Length (met): {avg_msg_len:.1f} chars")

# Quadrants analysis
print("\n📊 Your Meeting Success by Quadrant:")
quadrants = {
    'Short & Curious': [],
    'Short & Silent': [],
    'Long & Curious': [],
    'Long & Silent': []
}

for d in valid_data:
    q_density = d.get('question_density_first10')
    msg_len = d.get('median_len_first10')
    met = d.get('met')

    if q_density is not None and msg_len is not None:
        is_curious = q_density > 0.3
        is_long = msg_len > 120

        if is_curious and not is_long:
            quadrant = 'Short & Curious'
        elif is_curious and is_long:
            quadrant = 'Long & Curious'
        elif not is_curious and is_long:
            quadrant = 'Long & Silent'
        else:
            quadrant = 'Short & Silent'

        quadrants[quadrant].append(met)

for q_name, outcomes in quadrants.items():
    if outcomes:
        yes_count = sum(1 for o in outcomes if o == 'Yes')
        total = len(outcomes)
        rate = (yes_count / total * 100) if total > 0 else 0
        print(f"   {q_name}: {yes_count}/{total} ({rate:.1f}%)")

# Generate JSON summary for dashboard
summary = {
    'total_conversations': total_convos,
    'met_count': meet_count,
    'meet_rate': round(meet_rate, 1),
    'concrete_met': len(concrete_invites),
    'non_concrete_met': len(non_concrete_invites),
    'avg_invite_index': round(avg_invite_index, 1) if invite_indices else None,
    'avg_question_density': round(avg_q_density, 2) if question_densities else None,
    'avg_msg_length': round(avg_msg_len, 1) if msg_lengths else None,
    'quadrant_stats': {
        name: {
            'met': sum(1 for o in outcomes if o == 'Yes'),
            'total': len(outcomes),
            'rate': round((sum(1 for o in outcomes if o == 'Yes') / len(outcomes) * 100) if outcomes else 0, 1)
        }
        for name, outcomes in quadrants.items() if outcomes
    }
}

# Save to file
output_path = Path(__file__).parent / 'data' / 'personal_stats.json'
with open(output_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n✅ Personal stats saved to {output_path}")
