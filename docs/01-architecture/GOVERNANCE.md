# 📋 AI Agent Governance Framework
**Version:** 2.1.0 | **Last Updated:** 2026-01-03 | **Author:** Quievreux Consulting

---

## 🎯 Executive Summary

This framework establishes mandatory standards for AI agents creating code in Git projects. It covers documentation practices, package management (PNPM), semantic versioning, and Next.js development patterns. All AI agents working on Quievreux projects MUST follow these guidelines.

**Core Principles:**
1. **Structure Before Code** – 80% planning saves 200% development time
2. **Consistency Over Creativity** – Follow established patterns
3. **Automation First** – Never do manually what can be automated
4. **Documentation as Code** – Treat docs with the same rigor as source code

---

## 📑 Table of Contents

1. [Package Manager Standards (PNPM)](#-1-package-manager-standards-pnpm)
2. [Documentation Structure](#-2-documentation-structure)
3. [Version Management & Semantic Release](#-3-version-management--semantic-release)
4. [Next.js Development Standards](#-4-nextjs-development-standards)
5. [Project Architecture](#-5-project-architecture)
6. [Code Quality & Testing](#-6-code-quality--testing)
7. [Deployment & CI/CD](#-7-deployment--cicd)
8. [AI Agent Behavioral Rules](#-8-ai-agent-behavioral-rules)
9. [Templates & References](#-9-templates--references)
10. [Troubleshooting](#-10-troubleshooting)

---

## 📦 1. Package Manager Standards (PNPM)

### 1.1 Core Requirements

```yaml
# MANDATORY for all projects:
Package Manager: pnpm (Version 10.0.0+)

# PROHIBITED:
❌ NEVER use npm
❌ NEVER use yarn
❌ NEVER commit package-lock.json
❌ NEVER commit yarn.lock
```

### 1.2 Package.json Configuration

```json
{
  "packageManager": "pnpm@10.11.0+sha512.6540583f41cc5f628eb3d9773ecee802f4e9ef2e4cfcb3914c57...",
  "engines": {
    "node": ">=22.0.0",
    "pnpm": ">=10.0.0"
  }
}
```

### 1.3 Migration Protocol
(Existing protocol...)

### 1.9 npm Publishing Strategy (NEW)

#### Phase 1: Solo Development (Current)
```yaml
Registry: npm (public)
Scope: @[your-npm-username] (e.g. @squievreux)
Cost: $0/month
Access: public
Automation: GitHub Actions + Semantic Release
```

**Setup:**
1. Configure `NPM_TOKEN` in GitHub Repository Secrets.
2. Use `.github/workflows/release-ui.yml` for automated releases.
3. Every merge to `main` with a `feat:` or `fix:` commit triggers a release.

#### migration Campaign: Bulk Update
For large-scale updates across many repositories (e.g., migrating @quievreux -> @squievreux), use the **Migration Campaign Action**:

1. Open `.github/workflows/migration-campaign.yml`.
2. Run workflow manually via `workflow_dispatch`.
3. Provide the list of repositories to update.
4. The bot will create PRs in all target repositories.

#### Phase 2: Team Growth (Future)
```yaml
Registry: npm (public)
Scope: @quievreux
Cost: $7/month
Access: public (or private if needed)

Example:
- @quievreux/ui
- @quievreux/utils
- @quievreux/core (private)
```

**Migration:**
```bash
# 1. Create npm Organisation:
npm.com → Organizations → Create

# 2. Publish new scoped package:
# Update package.json name: @quievreux/ui
pnpm publish --access public

# 3. Deprecate old package:
npm deprecate @squievreux/ui "Moved to @quievreux/ui"

# 4. Bulk update apps:
find apps -name package.json \
  -exec sed -i 's/@squievreux/@quievreux/g' {} \;
```

---

### 8.1 Package Management Rules
(Existing rules...)

### 8.4 Git & Conflict Resolution (Standard Workflow)
Um Konflikte zu vermeiden und eine saubere Historie zu garantieren, ist folgender Workflow für alle Agents und Developer verpflichtend:

1. **Local Sync**: `git pull --rebase origin <branch>`
2. **Conflict Handling**:
   - Manuelle Korrektur der Konfliktmarker
   - `git add <file>`
   - `git rebase --continue`
3. **Final Push**: `git push`

❌ **VERBOTEN**: `git merge` von Remote-Änderungen in Feature-Branches (verursacht unnötige Merge-Commits).

(Rest of the framework...)
