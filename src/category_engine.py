"""Category engine for activity classification."""

import datetime
import json
import os
from collections import defaultdict

# Standard Kategorien mit Keywords
ACTIVITY_CATEGORIES = {
    "Essen": {
        "keywords": [
            "frühstück",
            "mittagessen",
            "abendessen",
            "essen",
            "snack",
            "kaffee",
            "trinken",
            "pause",
            "lunch",
        ],
        "priority": 10,
    },
    "Jobsuche": {
        "keywords": [
            "jobsuche",
            "bewerbung",
            "freelancer",
            "upwork",
            "xing",
            "linkedin",
            "karriere",
            "freelancermap",
        ],
        "priority": 9,
    },
    "Meetings": {
        "keywords": [
            "diskussion",
            "meeting",
            "call",
            "gespräch",
            "besprechung",
            "zoom",
            "teams",
            "standup",
            "sync",
        ],
        "priority": 8,
    },
    "Entwicklung": {
        "keywords": [
            "code",
            "programmieren",
            "entwicklung",
            "bug",
            "feature",
            "webapp",
            "app",
            "software",
            "deploy",
        ],
        "priority": 7,
    },
    "Dokumentation": {
        "keywords": [
            "dokumentation",
            "docs",
            "readme",
            "anleitung",
            "erklärung",
            "beschreibung",
            "dokumentieren",
        ],
        "priority": 6,
    },
    "KI/Automation": {
        "keywords": [
            "ki",
            "claude",
            "chatgpt",
            "langdock",
            "n8n",
            "automation",
            "ai",
            "gpt",
            "gemini",
        ],
        "priority": 5,
    },
    "Lernen": {
        "keywords": [
            "lernen",
            "einarbeitung",
            "tutorial",
            "kurs",
            "kennen gelernt",
            "studieren",
            "eingearbeitet",
        ],
        "priority": 4,
    },
    "Schreiben": {
        "keywords": [
            "tagebuch",
            "blog",
            "artikel",
            "schreiben",
            "notizen",
            "text",
            "geschrieben",
        ],
        "priority": 3,
    },
    "Recherche": {
        "keywords": [
            "recherche",
            "suchen",
            "googeln",
            "anschauen",
            "prüfen",
            "vergleichen",
        ],
        "priority": 2,
    },
    "Sonstiges": {"keywords": [], "priority": 1},
}


class CategoryEngine:
    """Engine für Activity-Kategorisierung"""

    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/Documents/StayOnTrack")

        self.config_dir = config_dir
        self.learned_keywords_file = os.path.join(config_dir, "learned_keywords.json")
        self.learned_keywords = self._load_learned_keywords()

    def _load_learned_keywords(self):
        """Lädt gelernte Keywords aus JSON-Datei"""
        if not os.path.exists(self.learned_keywords_file):
            return {"learned_keywords": {}, "ignored_phrases": []}

        try:
            with open(self.learned_keywords_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"learned_keywords": {}, "ignored_phrases": []}

    def _save_learned_keywords(self):
        """Speichert gelernte Keywords"""
        self.learned_keywords["last_updated"] = datetime.datetime.now().isoformat()

        with open(self.learned_keywords_file, "w", encoding="utf-8") as f:
            json.dump(self.learned_keywords, f, indent=2, ensure_ascii=False)

    def _merge_keywords(self):
        """Kombiniert Standard-Keywords mit gelernten Keywords"""
        merged = {}

        # Start mit Standard-Keywords
        for category, config in ACTIVITY_CATEGORIES.items():
            merged[category] = config["keywords"].copy()

        # Füge gelernte Keywords hinzu
        for category, data in self.learned_keywords.get("learned_keywords", {}).items():
            if category in merged:
                merged[category].extend(data.get("keywords", []))
            else:
                merged[category] = data.get("keywords", [])

        return merged

    def categorize_activity(self, activity_text):
        """
        Kategorisiert eine Aktivität basierend auf Keywords

        Returns: (category_name, confidence_score)
        """
        text_lower = activity_text.lower()
        all_keywords = self._merge_keywords()

        matches = []

        for category, config in ACTIVITY_CATEGORIES.items():
            if category == "Sonstiges":
                continue

            # Hole alle Keywords (Standard + gelernte)
            keywords = all_keywords.get(category, [])

            # Zähle Keyword-Treffer
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)

            if keyword_matches > 0:
                # Score = Anzahl Treffer * Priorität
                score = keyword_matches * config["priority"]
                matches.append((category, score, keyword_matches))

        if not matches:
            return ("Sonstiges", 0)

        # Sortiere nach Score (höchster zuerst)
        matches.sort(key=lambda x: x[1], reverse=True)

        best_match = matches[0]
        return (best_match[0], best_match[1])

    def get_category_breakdown(self, entries):
        """
        Analysiert Zeitverteilung pro Kategorie

        Args:
            entries: List of entry dicts with 'activity' key

        Returns:
        {
            "Entwicklung": {"count": 12, "percentage": 35.3, "entries": [...]},
            ...
        }
        """
        categorized = {}
        total = len(entries)

        if total == 0:
            return {}

        for entry in entries:
            # Support both dict entries (new) and list entries (legacy)
            if isinstance(entry, dict):
                activity = entry.get("activity", "")
            elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                activity = entry[1]
            else:
                continue

            category, score = self.categorize_activity(activity)

            if category not in categorized:
                categorized[category] = {"count": 0, "entries": [], "scores": []}

            categorized[category]["count"] += 1
            categorized[category]["entries"].append(entry)
            categorized[category]["scores"].append(score)

        # Berechne Prozentsätze und durchschnittliche Scores
        for category in categorized:
            count = categorized[category]["count"]
            categorized[category]["percentage"] = round(count / total * 100, 1)

            scores = categorized[category]["scores"]
            categorized[category]["avg_score"] = round(sum(scores) / len(scores), 1)

        # Sortiere nach Anzahl (absteigend)
        sorted_categories = dict(
            sorted(categorized.items(), key=lambda x: x[1]["count"], reverse=True)
        )

        return sorted_categories


class AutoLearner:
    """Automatisches Lernen neuer Keywords"""

    def __init__(self, storage_manager, category_engine):
        self.storage = storage_manager
        self.engine = category_engine

    def analyze_unknown_entries(self, days=30):
        """
        Findet häufige Phrasen in unkategorisierten Einträgen

        Returns: (frequent_phrases, uncategorized_entries)
        """
        # Hole alle Einträge der letzten N Tage
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days - 1)

        entries_by_date = self.storage.get_date_range_entries(start_date, end_date)

        uncategorized = []
        phrase_counts = defaultdict(int)

        for _date, day_entries in entries_by_date.items():
            for entry in day_entries:
                # Support both dict entries (new) and list entries (legacy)
                if isinstance(entry, dict):
                    activity = entry.get("activity", "")
                elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                    activity = entry[1]
                else:
                    continue

                category, score = self.engine.categorize_activity(activity)

                # Nur "Sonstiges" oder niedrige Scores
                if category == "Sonstiges" or score < 3:
                    uncategorized.append(activity)

                    # Extrahiere 1-3 Wort-Phrasen
                    words = activity.lower().split()
                    for length in [1, 2, 3]:
                        for i in range(len(words) - length + 1):
                            phrase = " ".join(words[i : i + length])
                            # Filtere zu kurze Phrasen und Stoppwörter
                            if len(phrase) > 3 and not self._is_stopword(phrase):
                                phrase_counts[phrase] += 1

        # Finde häufige Phrasen (>= 3 Vorkommen)
        frequent_phrases = {phrase: count for phrase, count in phrase_counts.items() if count >= 3}

        return frequent_phrases, uncategorized

    def _is_stopword(self, phrase):
        """Filtert häufige Füllwörter"""
        stopwords = [
            "der",
            "die",
            "das",
            "und",
            "oder",
            "mit",
            "für",
            "von",
            "zu",
            "im",
            "am",
            "auf",
            "ein",
            "eine",
        ]
        return phrase in stopwords

    def suggest_category_for_phrase(self, phrase):
        """
        Schlägt Kategorie basierend auf Wort-Ähnlichkeit vor

        Returns: (category_name, confidence)
        """
        suggestions = []

        # Regel 1: Zeitbezogene Wörter → Essen
        time_indicators = ["pause", "mittag", "morgen", "abend", "frühstück"]
        if any(indicator in phrase for indicator in time_indicators):
            suggestions.append(("Essen", 0.8))

        # Regel 2: Meeting-Wörter → Meetings
        meeting_indicators = ["meeting", "call", "gespräch", "standup", "sync", "daily"]
        if any(indicator in phrase for indicator in meeting_indicators):
            suggestions.append(("Meetings", 0.9))

        # Regel 3: Code-Wörter → Entwicklung
        dev_indicators = ["code", "review", "bug", "feature", "deploy", "commit", "pull"]
        if any(indicator in phrase for indicator in dev_indicators):
            suggestions.append(("Entwicklung", 0.85))

        # Regel 4: Lern-Wörter → Lernen
        learn_indicators = ["lernen", "tutorial", "kurs", "einarbeitung", "kennen"]
        if any(indicator in phrase for indicator in learn_indicators):
            suggestions.append(("Lernen", 0.8))

        # Regel 5: Schreib-Wörter → Schreiben
        write_indicators = ["schreiben", "artikel", "blog", "text", "notiz"]
        if any(indicator in phrase for indicator in write_indicators):
            suggestions.append(("Schreiben", 0.75))

        # Sortiere nach Confidence
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[0] if suggestions else ("Sonstiges", 0.5)

    def add_learned_keyword(self, phrase, category, auto=False):
        """Fügt ein gelerntes Keyword hinzu"""
        if "learned_keywords" not in self.engine.learned_keywords:
            self.engine.learned_keywords["learned_keywords"] = {}

        if category not in self.engine.learned_keywords["learned_keywords"]:
            self.engine.learned_keywords["learned_keywords"][category] = {
                "keywords": [],
                "learned_from": "auto_analysis" if auto else "user_feedback",
                "usage_count": 0,
            }

        # Füge Keyword hinzu, wenn noch nicht vorhanden
        keywords = self.engine.learned_keywords["learned_keywords"][category]["keywords"]
        if phrase not in keywords:
            keywords.append(phrase)
            self.engine.learned_keywords["learned_keywords"][category]["usage_count"] += 1
            self.engine._save_learned_keywords()
            return True

        return False
