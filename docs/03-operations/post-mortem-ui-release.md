---
title: "Post-Mortem: @squievreux/ui Initial Release"
type: "operations"
audience: "developer"
status: "approved"
priority: "medium"
version: "1.0.0"
created: "2025-12-30"
updated: "2025-12-30"
tags: ["post-mortem", "release", "git", "npm", "ci"]
---

# Post-Mortem: Initial Release of @squievreux/ui

## 1. Executive Summary

The initial setup and release of the `@squievreux/ui` package encountered several friction points, primarily revolving around **dependency resolution (Peer Dependencies)**, **CI environment configuration**, and **Git branch management**.

This document summarizes the root causes, the solutions applied, and the lessons learned to improve future package scaffolding.

---

## 2. Issues & Root Causes

### 🔴 Issue 1: Dependency Conflict (React Versions)

**Symptom:**  
`npm install` failed in CI with `ERESOLVE unable to resolve dependency tree`.

**Root Cause:**
*   The package declared `react` and `react-dom` as `peerDependencies` (correct).
*   However, `react` was pinned to `^18.2.0` in `devDependencies`, but `react-dom` was **missing** from `devDependencies`.
*   NPM tried to install the latest `react-dom` (v19.x) to satisfy the peer dependency, which clashed with the installed `react` v18.

**Solution:**
*   Explicitly added `"react-dom": "^18.2.0"` to `devDependencies`.
*   Removed the `--legacy-peer-deps` flag from CI, as the tree was now valid.

### 🔴 Issue 2: Git Merge Conflicts & Dirty State

**Symptom:**
Repeated merge conflicts when pushing branches, specifically involving `.npmrc`.

**Root Cause:**
*   A local `.npmrc` containing auth tokens was created but then causally tracked/untracked.
*   The remote `main` branch state drifted from the local feature branch.
*   Attempting to rebase "dirty" branches led to a loop of conflicts.

**Solution:**
*   **Clean Slate Strategy:** Deleted the conflict-ridden branches.
*   Checked out a fresh `feat/ui-design-system-clean` branch from `origin/main`.
*   Re-applied only the necessary file changes without the Git history baggage.

### 🔴 Issue 3: Missing CI Configuration Files

**Symptom 1:** `actions/setup-node` failed because it couldn't find `packages/ui/package-lock.json`.  
**Symptom 2:** `npm run lint` failed with `eslint: not found`.

**Root Cause:**
*   **Lockfile:** The `package-lock.json` was initially not committed.
*   **Linter:** `eslint` was defined in `scripts`, but the binary was not installed in `devDependencies`.

**Solution:**
*   Generated and committed `package-lock.json`.
*   Configured the CI workflow to use a wildcard path `**/package-lock.json` for robustness.
*   Installed `eslint`, `globals`, and `typescript-eslint` and migrated to the new `eslint.config.mjs` (Flat Config).

---

## 3. Lessons Learned & Action Items

### ✅ Better Scaffolding
*   **Explicit DevDeps:** When creating a library, **always** match `peerDependencies` with `devDependencies` of the same version immediately to avoid NPM resolution guesswork.
*   **Linting from Start:** Include `eslint` installation and configuration in the initial scaffolding script, not as an afterthought.

### ✅ Git Hygiene
*   **Ignore Early:** Add sensitive or environment-specific files (like `.npmrc`) to `.gitignore` **before** the first commit.
*   **Abort & Restart:** If a branch gets entangled in complex merge conflicts involving deleted/untracked files, it is often faster to cherry-pick changes to a clean branch than to fight the history.

### ✅ CI Robustness
*   **Lockfiles are Mandatory:** Never push a package definition without its lockfile. CI needs it for reproducible builds and caching.
*   **Test Locally:** Run `npm install` and `npm run lint` in a clean environment (or container) before pushing to verify the build chain works from scratch.

---

## 4. Conclusion

The pipeline is now stable. The architecture follows a clean separation of concerns, uses modern tooling (ESLint 9, React 18 strictness), and the deployment automate is fully functional without "hacks".
