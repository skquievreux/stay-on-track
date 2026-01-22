# Analytics & Activity Categories

## Overview

Stay-On-Track automatically categorizes your activities into 9 predefined categories using keyword matching and machine learning.

## The 9 Categories

### 🍽️ Essen (Food & Breaks)
**Keywords:** frühstück, mittagessen, abendessen, pause, kaffee, snack

**Examples:**
- "Frühstück"
- "Mittagspause"
- "Kaffee trinken"

### 💼 Jobsuche (Job Search)
**Keywords:** jobsuche, bewerbung, linkedin, xing, freelancer

**Examples:**
- "Jobsuche Freelancermap"
- "Bewerbung schreiben"
- "LinkedIn Profil aktualisieren"

### 💬 Meetings (Meetings & Discussions)
**Keywords:** meeting, call, diskussion, besprechung, standup

**Examples:**
- "Meeting mit Team"
- "Daily Standup"
- "Kundengespräch"

### 🛠️ Entwicklung (Development)
**Keywords:** code, entwicklung, programmieren, debug, refactor

**Examples:**
- "Code schreiben"
- "Bug fixen"
- "Feature implementieren"

### 📝 Dokumentation (Documentation)
**Keywords:** dokumentation, readme, wiki, anleitung

**Examples:**
- "README aktualisieren"
- "API Dokumentation"
- "Anleitung schreiben"

### 🤖 KI/Automation (AI & Automation)
**Keywords:** ki, ai, claude, chatgpt, automation, langdock

**Examples:**
- "Claude fragen"
- "Langdock einarbeitung"
- "Automation Script erstellen"

### 📚 Lernen (Learning)
**Keywords:** lernen, tutorial, kurs, training, einarbeitung

**Examples:**
- "Python Tutorial"
- "Neues Framework lernen"
- "Einarbeitung in Tool X"

### ✍️ Schreiben (Writing)
**Keywords:** schreiben, artikel, blog, tagebuch

**Examples:**
- "Tagebuch schreiben"
- "Blog-Artikel verfassen"
- "Notizen machen"

### 🔍 Recherche (Research)
**Keywords:** recherche, suchen, analysieren, evaluieren

**Examples:**
- "Tool-Recherche"
- "Competitor Analysis"
- "Technologie evaluieren"

## Auto-Learning System

### How It Works

1. **Keyword Matching**
   - Each activity is checked against predefined keywords
   - Case-insensitive matching
   - Partial word matching

2. **Pattern Discovery**
   - Every 7 days, the system analyzes uncategorized entries
   - Identifies frequently used phrases
   - Suggests new keywords

3. **User Feedback**
   - You can accept or reject suggestions
   - Accepted keywords are saved to `learned_keywords.json`

### Learned Keywords File

**Location:** `C:\Users\YourName\Documents\StayOnTrack\learned_keywords.json`

**Format:**
```json
{
  "learned_keywords": {
    "💬 Meetings": {
      "keywords": ["standup", "daily", "retrospektive"],
      "usage_count": 15
    },
    "🛠️ Entwicklung": {
      "keywords": ["pr review", "merge", "deploy"],
      "usage_count": 23
    }
  }
}
```

### Managing Learned Keywords

**To add custom keywords:**
1. Open `learned_keywords.json`
2. Add keywords to the appropriate category
3. Save the file
4. Restart Stay-On-Track

**To reset learned keywords:**
1. Delete `learned_keywords.json`
2. Restart Stay-On-Track
3. File will be recreated with defaults

## Analytics Dashboard

### Summary Statistics

**Total Entries**
- Count of all logged activities in the selected period

**Average Entries/Day**
- Total entries ÷ number of days

**Most Productive Day**
- Day with the highest number of entries

**Most Active Hour**
- Hour with the most activity (e.g., "10:00-11:00")

### Category Breakdown

Visual bar chart showing:
- Percentage of activities per category
- Color-coded bars
- Sorted by frequency

**Example:**
```
🤖 KI/Automation    ████████████ 22%
📚 Lernen          ████████     17%
💼 Jobsuche        ████████     17%
📝 Dokumentation   ████████     17%
💬 Meetings        ████████     17%
🍽️ Essen          █████        11%
```

### Daily Breakdown

Bar chart showing activity per day:
- X-axis: Dates
- Y-axis: Number of entries
- Color: Category distribution

### Activity Heatmap

Shows your top 5 most active hours:
```
10:00-11:00  ████████████████████ 15 entries
14:00-15:00  ████████████████     12 entries
09:00-10:00  ██████████████       11 entries
```

## Interpreting Your Data

### High Activity Days
- Indicates focused work sessions
- Good for identifying productive patterns

### Low Activity Days
- May indicate meetings/deep work
- Or simply forgetting to log

### Category Distribution
- Balanced: Good variety of tasks
- Skewed: May indicate focus area or imbalance

### Peak Hours
- Identify your most productive times
- Schedule important work accordingly

## Tips for Better Analytics

### Be Consistent
- Log activities regularly
- Don't skip reminders

### Be Descriptive
- Use clear, searchable terms
- Include project names when relevant

### Review Weekly
- Check analytics every Friday
- Adjust work patterns based on insights

### Customize Categories
- Add keywords for your specific workflow
- Review and update learned keywords monthly

---

**Next:** [Troubleshooting](../03-operations/troubleshooting.md) | [Back to User Guide](user-guide.md)
