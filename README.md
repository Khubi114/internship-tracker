# Student Internship Application Tracker

Flask + PostgreSQL web app used to demonstrate a CI/CD pipeline (SWE40006, Team CL06G05).

## Pipeline
`lint-and-unit` -> `build-and-push` -> `deploy-staging` -> `e2e-tests` -> `deploy-production`

Every push is linted and unit tested, then built into a Docker image pushed to GHCR
(`ghcr.io/khubi114/internship-tracker:<commit SHA>`, plus `:latest` on `main`).

## Layout
- `app/` Flask application
- `tests/unit`, `tests/integration`, `tests/e2e`
- `Dockerfile` (Gunicorn), `docker-compose.yml` (web + PostgreSQL)
- `.github/workflows/pipeline.yml`

## Working rules
`main` is protected. Branch, open a Pull Request, get one approval and a green `lint-and-unit`, then merge.
B and C add their own jobs to `pipeline.yml` through PRs; Khubi reviews and merges.

## Local run
```
pip install -r requirements-dev.txt
ruff check . && pytest tests/unit --cov=app --cov-fail-under=80
docker build -t internship-tracker . && docker run -p 8000:8000 internship-tracker
```
