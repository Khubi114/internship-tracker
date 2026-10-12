# Khubi setup checklist

1. Create the repo on GitHub (empty, no README), then from this folder:
   `git init -b main && git add . && git commit -m "Initial repo, pipeline skeleton, Dockerfile"`
   `git remote add origin git@github.com:OWNER/REPO.git && git push -u origin main`
   (Branch protection is not on yet, so this first push to main is allowed.)
2. Add teammates as collaborators (Settings > Collaborators), with Write access.
3. Run `./scripts/setup-repo.sh OWNER/REPO`. It protects main, creates the staging and
   production environments, and sets the six secrets.
   Note: branch protection on a private repo needs GitHub Pro/Team; on the free plan make the repo public.
4. The GHCR token is a classic PAT with `write:packages` (and `read:packages`). After the first
   push, open the package on GitHub > Package settings and make sure the repo has access.
5. Tell B, C and D: branch from main, open a PR, Khubi reviews and merges. B and C replace the
   TODO steps in their own jobs only.

## Secrets
| Secret | Used by |
|---|---|
| GHCR_USERNAME, GHCR_TOKEN | build-and-push (push); B's deploy jobs (docker login on the server) |
| SSH_PRIVATE_KEY | B's deploy jobs |
| STAGING_HOST, PROD_HOST | B's deploy jobs |
| STAGING_URL | C's e2e-tests |

## Image tags
Every push: `ghcr.io/khubi114/internship-tracker:<commit SHA>`. Pushes to main also get `:latest`.
