#!/usr/bin/env bash
# Restores the last image that passed its smoke check. Called by the job's
# "Automatic rollback" step when deploy.sh fails.
set -euo pipefail
cd ~/app

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
log() { echo "$(date -Is) $*" | tee -a deploy-history.log; }

PREV_IMAGE=$(cat .deployed_image 2>/dev/null || true)
if [ -z "$PREV_IMAGE" ]; then
  log "ROLLBACK_FAILED no previous good image recorded"; exit 1
fi

START=$(date +%s)
log "ROLLBACK_START to=$PREV_IMAGE"

sed -i "s|^IMAGE=.*|IMAGE=$PREV_IMAGE|" .env
unset WEB_DB_PASSWORD   # make sure the rehearsal fault is not carried over

$COMPOSE pull web
$COMPOSE up -d --wait --wait-timeout 120
curl -fsS --max-time 5 --retry 5 --retry-delay 3 --retry-all-errors \
  http://localhost/health > /dev/null

log "ROLLBACK_OK image=$PREV_IMAGE seconds=$(( $(date +%s) - START ))"
