# Best Practices: Stay-On-Track Development

## Übersicht

Dieses Dokument beschreibt die bewährten Praktiken für die Entwicklung und Wartung des Stay-On-Track Projekts.

## Lokale Entwicklung

### Vor jedem Commit

**IMMER** das lokale Test-Skript ausführen:

```cmd
test-local.bat
```

Dieses Skript prüft:
- ✅ Code-Qualität (Pylint 10/10)
- ✅ Build-Erfolg (PyInstaller)
- ✅ Executable-Erstellung

### Manuelle Tests

```cmd
# Nur Pylint
pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401

# Nur Build
pyinstaller build.spec --clean

# Installer kompilieren (optional, benötigt Inno Setup)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss
```

## Code-Qualität Standards

### Pylint-Konfiguration

**Deaktivierte Checks:**
- `C0114, C0115, C0116` - Docstrings (optional für kleine Projekte)
- `R0903` - Too few public methods
- `W0702` - Bare except
- `E0401` - Import errors (unvermeidbar in CI)

**Ziel:** 10.00/10 Rating

### Code-Style

```python
# ✅ RICHTIG: Encoding angeben
with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)

# ❌ FALSCH: Kein encoding
with open(file, "r") as f:
    data = json.load(f)

# ✅ RICHTIG: Ungenutzte Parameter mit _ prefixen
def callback(self, _unused_param):
    pass

# ❌ FALSCH: Ungenutzte Parameter ohne _
def callback(self, unused_param):
    pass
```

### Trailing Whitespace

**Vermeiden Sie trailing whitespace!**
- Konfigurieren Sie Ihren Editor, um diese automatisch zu entfernen
- VS Code: `"files.trimTrailingWhitespace": true`

## Git Workflow

### Branch-Strategie

```bash
# Feature entwickeln
git checkout -b feature/mein-feature
# ... Änderungen machen ...
test-local.bat  # WICHTIG!
git add .
git commit -m "feat: beschreibung"
git push origin feature/mein-feature

# Pull Request erstellen auf GitHub
# Nach Review: Merge in main
```

### Commit Messages

Verwenden Sie [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: neue Funktion hinzugefügt
fix: Bug behoben
docs: Dokumentation aktualisiert
chore: Wartungsarbeiten
refactor: Code umstrukturiert
test: Tests hinzugefügt
```

## CI/CD Pipeline

### Automatischer Build

Bei jedem Push zu `main`:
1. Pylint Code-Analyse
2. PyInstaller Build
3. Inno Setup Installer-Kompilierung
4. Artifact-Upload

### Installer Download

Nach erfolgreichem Build:
1. https://github.com/skquievreux/stay-on-track/actions
2. Neuesten erfolgreichen Run auswählen
3. "Artifacts" → `StayOnTrack-Installer` herunterladen

## Projekt-Struktur

```
Stay-On-Track/
├── src/                    # Python Source Code
│   ├── main.py            # Entry Point
│   ├── config.py          # Konfigurationsverwaltung
│   ├── storage.py         # CSV-Speicherung
│   ├── scheduler.py       # Timer-Logik
│   └── ui.py              # GUI-Komponenten
├── docs/                   # Dokumentation
│   └── 02-implementation/ # Dieser Ordner
├── .github/workflows/      # CI/CD
│   └── ci.yml             # Build Pipeline
├── build.spec             # PyInstaller Config
├── setup_script.iss       # Inno Setup Config
├── test-local.bat         # Lokales Test-Skript
└── requirements.txt       # Python Dependencies
```

## Häufige Probleme

### Problem: Pylint schlägt fehl

**Lösung:**
```cmd
# Lokal testen
pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401

# Fehler beheben, dann erneut testen
test-local.bat
```

### Problem: PyInstaller Build schlägt fehl

**Lösung:**
```cmd
# Clean build
pyinstaller build.spec --clean

# Prüfen ob alle Dependencies installiert sind
pip install -r requirements.txt
```

### Problem: Import-Fehler in CI

**Lösung:**
- E0401 ist bereits in `.github/workflows/ci.yml` deaktiviert
- Lokal sollten keine Import-Fehler auftreten

## Deployment

### Lokale Installation testen

1. Installer von GitHub Actions herunterladen
2. In sauberer Umgebung installieren (z.B. VM)
3. Funktionalität testen:
   - Auto-Start
   - System Tray Icon
   - 15-Minuten-Timer
   - CSV-Speicherung in `~/Documents/StayOnTrack/`

### Release-Prozess

1. Alle Tests lokal bestanden
2. CI-Build erfolgreich
3. Installer manuell getestet
4. GitHub Release erstellen mit Installer als Asset

## Wartung

### Regelmäßige Aufgaben

**Wöchentlich:**
- Dependencies aktualisieren: `pip list --outdated`
- CI-Logs überprüfen

**Monatlich:**
- Python-Version aktualisieren (wenn nötig)
- Inno Setup aktualisieren
- Dokumentation überprüfen

## Kontakt & Support

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/skquievreux/stay-on-track/issues
- Dokumentation: `/docs` Ordner

---

**Letzte Aktualisierung:** 2026-01-16
**Version:** 1.0.0
