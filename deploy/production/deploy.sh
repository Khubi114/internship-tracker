#!/usr/bin/env bash
# Production deploy with smoke check. Called by the deploy-production job.
# Usage: deploy.sh <full-image-ref> [simulate-bad-release 0|1]
#   e.g. deploy.sh ghcr.io/owner/repo:3f2c1ab... 0
set -euo pipefail
cd ~/app

NEW_IMAGE="$1"
SIMULATE="${2:-0}"
SMOKE_PATH="${SMOKE_PATH:-/}"   # a page that reads from the database
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
log() { echo "$(date -Is) $*" | tee -a deploy-history.log; }

test -f .env
PREV_IMAGE=$(cat .deployed_image 2>/dev/null || echo none)
log "DEPLOY_START new=$NEW_IMAGE prev=$PREV_IMAGE"

# Point Compose at the new image (same .env approach as staging)
if grep -q '^IMAGE=' .env; then
  sed -i "s|^IMAGE=.*|IMAGE=$NEW_IMAGE|" .env
else
  echo "IMAGE=$NEW_IMAGE" >> .env
fi

# Rollback rehearsal: give the new web container a wrong DB password,
# so /health fails in production only (a prod-only config fault).
if [ "$SIMULATE" = "1" ]; then
  export WEB_DB_PASSWORD="deliberately-wrong"
  log "SIMULATED_BAD_RELEASE"
fi

$COMPOSE pull web
if ! $COMPOSE up -d --wait --wait-timeout 120; then
  log "DEPLOY_FAILED containers not healthy"; exit 1
fi

# Smoke check (brief Stage 4)
curl -fsS --max-time 5 --retry 5 --retry-delay 3 --retry-all-errors \
  http://localhost/health > /dev/null || { log "DEPLOY_FAILED /health"; exit 1; }
curl -fsS --max-time 5 -o /dev/null "http://localhost${SMOKE_PATH}" \
  || { log "DEPLOY_FAILED ${SMOKE_PATH}"; exit 1; }

# Only a deploy that passes becomes the rollback target
echo "$NEW_IMAGE" > .deployed_image
log "DEPLOY_OK image=$NEW_IMAGE"

# Old images fill the disk; GHCR keeps every tag, so rollback can re-pull
docker image prune -af --filter "until=168h" > /dev/null || true
