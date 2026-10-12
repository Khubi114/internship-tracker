#!/usr/bin/env bash
# Khubi: one-off GitHub setup. Needs the GitHub CLI, logged in with: gh auth login
# Usage: ./scripts/setup-repo.sh OWNER/REPO
set -euo pipefail
REPO="${1:?Usage: $0 OWNER/REPO}"

echo "== Protect main (PR + 1 approval + passing lint-and-unit, branch up to date) =="
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<JSON
{
  "required_status_checks": { "strict": true, "contexts": ["lint-and-unit"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

echo "== Create staging and production environments =="
gh api -X PUT "repos/$REPO/environments/staging" >/dev/null
gh api -X PUT "repos/$REPO/environments/production" >/dev/null

echo "== Repository secrets (values are typed here, never stored in the repo) =="
read -r -p  "GHCR username (GitHub username): "            GHCR_USERNAME
read -r -s -p "GHCR token (PAT with write:packages): "     GHCR_TOKEN; echo
read -r -p  "Staging server IP: "                          STAGING_HOST
read -r -p  "Production server IP: "                       PROD_HOST
read -r -p  "Staging URL (e.g. http://1.2.3.4): "          STAGING_URL
read -r -p  "Path to SSH private key file (.pem): "        KEY_FILE

gh secret set GHCR_USERNAME --repo "$REPO" --body "$GHCR_USERNAME"
gh secret set GHCR_TOKEN    --repo "$REPO" --body "$GHCR_TOKEN"
gh secret set STAGING_HOST  --repo "$REPO" --body "$STAGING_HOST"
gh secret set PROD_HOST     --repo "$REPO" --body "$PROD_HOST"
gh secret set STAGING_URL   --repo "$REPO" --body "$STAGING_URL"
gh secret set SSH_PRIVATE_KEY --repo "$REPO" < "${KEY_FILE/#\~/$HOME}"

echo "Done. Secrets now set:"; gh secret list --repo "$REPO"
