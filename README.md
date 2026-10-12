# ACEest Fitness & Gym — DevOps Assignment 1

A small Flask application for registering gym members and logging workouts. This repository demonstrates source control, automated tests, containerization, GitHub Actions CI, and a Jenkins pipeline.

## Features

- Register members with unique email addresses.
- Log workouts with a duration from 1 to 600 minutes.
- View members and the ten most recent workouts.
- Health endpoint at `/health` for container smoke tests.
- SQLite storage; set `DATABASE_PATH` to choose the database file.

## Run locally

Requires Python 3.10+ (CI and Docker use Python 3.12).

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python app.py
```

Open http://127.0.0.1:5000. Check http://127.0.0.1:5000/health for a JSON health response.

## Tests and lint

```bash
pytest -q
python -m compileall -q app.py tests
ruff check --select F app.py tests
```

The tests use a temporary SQLite database and do not modify your local gym data.

## Docker

Build and run:

```bash
docker build -t aceest-fitness:local .
docker run --rm -p 5000:5000 -v aceest-data:/data aceest-fitness:local
```

The container runs as a non-root user. The named volume persists the SQLite database under `/data`. Browse to http://127.0.0.1:5000.

## GitHub Actions

The workflow at `.github/workflows/main.yml` runs on pushes and pull requests. It checks Python syntax, runs Ruff's undefined/unused-name checks, executes pytest, builds the Docker image, and smoke-tests the `/health` endpoint. Review the **Actions** tab for actual run results; do not report a run as passing until it is green.

## Jenkins setup

1. In Jenkins, create a **Pipeline** job.
2. Under Pipeline, select **Pipeline script from SCM**.
3. Choose **Git**, enter this repository's clone URL, and select branch `*/main`.
4. Set Script Path to `Jenkinsfile`, save, then select **Build Now**.
5. The Jenkins agent needs Git, Python 3, permission to create virtual environments, and Docker CLI/daemon access.
6. Open the build's **Console Output** and confirm the Checkout, Syntax and lint, Pytest, and Docker build stages. Save screenshots of the successful build and console output for assignment evidence.

If Jenkins cannot access Docker, configure the lab's approved Docker access for the Jenkins agent rather than running Jenkins as root without review.

## Suggested manual test cases

1. Open the home page; verify the member and workout forms display.
2. Register a member using a valid name and email.
3. Register the same email again; verify a duplicate-email message appears.
4. Log a workout for the registered member with a valid duration.
5. Try a zero-minute workout; verify validation rejects it.
6. Request `/health`; expect HTTP 200 and `{"status":"ok"}`.

## Git workflow and submission evidence

Use meaningful commits for application, tests, container, and CI changes. For additional branch evidence, create a feature branch, make a small improvement, push it, and open a pull request so the pull-request workflow runs. Include screenshots of GitHub Actions and Jenkins successful runs in the assignment submission. The repository code and workflow configuration alone are not proof that Jenkins or GitHub Actions passed.

## Limitations

This is an educational sample, not a production-ready member-management system. Before production use, add authentication/authorization, CSRF protection, stronger deployment secrets, backups, and a production WSGI server.
