#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/publish_to_github.sh https://github.com/<user>/<repo>.git [branch]
# Example:
#   bash scripts/publish_to_github.sh https://github.com/alice/english-memory-ai.git work

REMOTE_URL="${1:-}"
BRANCH="${2:-$(git branch --show-current)}"

if [[ -z "$REMOTE_URL" ]]; then
  echo "Usage: bash scripts/publish_to_github.sh <repo_url> [branch]"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: current directory is not a git repository"
  exit 1
fi

if [[ -z "$BRANCH" ]]; then
  echo "Error: failed to detect current branch"
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote 'origin' already exists. Updating URL..."
  git remote set-url origin "$REMOTE_URL"
else
  echo "Adding remote 'origin'..."
  git remote add origin "$REMOTE_URL"
fi

echo "Pushing branch '$BRANCH' to origin..."
git push -u origin "$BRANCH"

echo "Done. Your code is now on GitHub (branch: $BRANCH)."
