#!/bin/bash

# ==============================================================================
# Migration Script: @quievreux/ui -> @squievreux/ui
# Usage: ./migrate-apps.sh "repo-name-1 repo-name-2 ..."
# Requirements: GitHub CLI (gh) installed and authenticated
# ==============================================================================

set -x # Enable debug mode

REPOS=$1

if [ -z "$REPOS" ]; then
  echo "Usage: $0 \"repo1 repo2 ...\""
  exit 1
fi

for REPO in $REPOS; do
  echo "----------------------------------------------------"
  echo "🚀 Migrating $REPO..."
  
  # 1. Clone
  echo "Cloning $REPO..."
  if [[ "$REPO" != */* ]]; then
    FULL_REPO="skquievreux/$REPO"
  else
    FULL_REPO="$REPO"
  fi
  
  gh repo clone "$FULL_REPO" "temp_$REPO" || { echo "❌ Failed to clone $FULL_REPO"; continue; }
  cd "temp_$REPO" || { echo "❌ Failed to enter temp_$REPO"; continue; }

  # 2. Branch
  git checkout -b chore/migrate-ui-scope || git checkout chore/migrate-ui-scope

  # 3. Perform Migration
  echo "📦 Updating dependencies..."
  # Use pnpm if pnpm-lock.yaml exists, otherwise npm
  if [ -f "pnpm-lock.yaml" ]; then
    pnpm remove @quievreux/ui --silent || true
    pnpm add @squievreux/ui
  else
    npm uninstall @quievreux/ui || true
    npm install @squievreux/ui
  fi

  # 4. Remove .npmrc
  if [ -f ".npmrc" ]; then
    echo "🗑️ Removing .npmrc..."
    rm .npmrc
  fi

  # 5. Bulk Replace in Code
  echo "🔍 Replacing imports in source code..."
  # Find files containing the old scope, excluding node_modules and .git
  FILES=$(grep -rl "@quievreux/ui" . --exclude-dir=node_modules --exclude-dir=.git)
  if [ -n "$FILES" ]; then
    echo "Found files to update: $FILES"
    echo "$FILES" | xargs sed -i 's/@quievreux\/ui/@squievreux\/ui/g'
  else
    echo "No occurrences of @quievreux/ui found in source code."
  fi

  # 6. Commit & Push
  git add .
  if git diff --cached --quiet; then
    echo "No changes to commit for $REPO."
  else
    git commit -m "chore: migrate to @squievreux/ui and remove GPR authentication"
    
    # Configure auth for push
    if [ -n "$GH_TOKEN" ]; then
      git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/${FULL_REPO}.git"
    fi
    
    git push origin chore/migrate-ui-scope --force
  fi

  # 7. Create Pull Request
  # Check if PR already exists
  EXISTING_PR=$(gh pr list --head chore/migrate-ui-scope --json number --jq '.[0].number')
  if [ -z "$EXISTING_PR" ]; then
    gh pr create \
      --title "chore: migrate to @squievreux/ui" \
      --body "This PR migrates the Design System from the private @quievreux scope to the public @squievreux scope. It also removes the unnecessary .npmrc file." \
      --base main
  else
    echo "PR #$EXISTING_PR already exists for $REPO."
  fi

  # 8. Cleanup
  cd ..
  rm -rf "temp_$REPO"
  
  echo "✅ Finished $REPO"
done

echo "🎉 Migration campaign completed!"
