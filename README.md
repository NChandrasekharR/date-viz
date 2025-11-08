# Hinge Dating Data Visualization

A personal data visualization project analyzing Hinge dating app conversation patterns and success rates.

## Live Demo
View the scrollytelling visualization at: [Your GitHub Pages URL]

## Features

- 📊 **Personal Journey Dashboard** - Your complete dating funnel from matches to meetings
- 📈 **Conversion Funnel** - Animated visualization showing match → response → meeting rates
- ⏱️ **Activity Timeline** - Monthly message patterns over time
- 📉 **Survival Analysis** - Kaplan-Meier curves showing conversation lifespans
- 🎯 **Success Patterns** - What messaging strategies work best

## Your Data (Privacy Protected)

The visualization shows **aggregated statistics only**. No personal chat content is stored in this repo.

**Included (safe to commit):**
- `data/conversations_features.min.json` - Numerical features (message counts, timing)
- `data/personal_stats.json` - Aggregated success metrics
- `data/timeline_stats.json` - Message activity by time
- `data/funnel_stats.json` - Conversion funnel metrics

**Excluded (privacy protected):**
- `data/matches.json` - Contains actual chat messages (gitignored)

## Setup with Your Own Data

1. **Export your Hinge data:**
   - Settings → "Download My Data"
   - Wait for email with data export

2. **Place your matches.json file:**
   ```bash
   # Place your exported matches.json in the data/ folder
   cp ~/Downloads/matches.json data/
   ```

3. **Run analysis scripts:**
   ```bash
   python3 analyze_personal_stats.py
   python3 analyze_timeline.py
   python3 analyze_full_funnel.py
   ```

4. **View locally:**
   ```bash
   python3 -m http.server 8080
   # Open http://localhost:8080
   ```

## Scripts

- `analyze_personal_stats.py` - Compute meeting success rates and patterns
- `analyze_timeline.py` - Analyze messaging activity over time
- `analyze_full_funnel.py` - Complete conversion funnel analysis

## Privacy & Security

- ✅ No PII (Personal Identifiable Information) committed to git
- ✅ Actual chat messages stay local only
- ✅ Only aggregated statistics are public
- ✅ All analysis runs locally on your machine

## Technologies

- D3.js for data visualization
- Vanilla JavaScript for interactivity
- Python for data analysis
- Scrollama for scrollytelling

## Insights

Based on the analysis of 5,601 matches:
- Only 3.7% of matches lead to a response
- Of those who respond, 9.7% convert to meetings
- Conversations average 28.6 messages
- Short & curious messaging style shows best results

---

**Note:** This is a personal data project. Your `data/matches.json` file containing actual chat content should NEVER be committed to git.
