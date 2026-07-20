# Claude Instructions for Mission Leader Assistant

This file provides guidance to Claude Code when working on the **Mission Leader Assistant** project. Please read and follow these instructions carefully before making any changes.

---

## Project Overview

Mission Leader Assistant is a Python web application built with a custom HTTP handler framework. It helps mission leaders manage lunch calendars, visit calendars, baptism plans, and more. The backend is Python (no third-party web framework), the frontend is plain HTML/CSS/JavaScript, and data is stored either in Firestore (production) or a local JSON file (dev mode).

**Key source locations:**
- `src/app.py` — application entry point and route registration
- `src/core/` — core framework (base handler, store abstractions)
- `src/handlers/` — feature-specific request handlers
- `src/views/` — frontend assets (`index.html`, `script.js`, `styles.css`)
- `tests/` — Python unit tests (unittest)

---

## Building & Running

### Option 1 — Docker (recommended for local testing)

```bash
docker compose up --build
```

The app will be available at `http://localhost:8080` in dev mode (no Google Services required).

### Option 2 — Direct Python

```bash
python3 src/app.py --dev --host localhost
```

Use the `--dev` flag so the app uses local JSON file storage instead of Firestore. The `--host` flag is needed for Firebase auth to work correctly when not in dev mode.

### Dev mode notes

- In dev mode (`--dev`), `CalendarHandler.DEV = True` is set.
- The frontend fetches `/api/config` on startup and, in dev mode, skips Firebase authentication, using `user_id="local"` instead.
- No Google credentials or Firebase project are needed.

---

## Linting

The project uses **Pylint** with configuration in `.pylintrc`.

```bash
pip install pylint
pylint $(git ls-files '*.py')
```

Aim for zero Pylint warnings on all Python files before opening a PR.

---

## Testing

Tests are standard Python `unittest` tests located in the `tests/` directory.

```bash
python -m unittest discover -s tests -v
```

Run the full test suite after every change to catch regressions early.

---

## UI Development — Take Screenshots

Whenever you make changes to frontend components (`src/views/index.html`, `src/views/script.js`, `src/views/styles.css`):

1. Start the application (`docker compose up --build` or the nodemon command above).
2. Open `http://localhost:8080` in a browser.
3. **Take a screenshot** of the affected UI state(s) and include it in your PR description or comment so the reviewer can verify the visual outcome without running the app locally.

---

## Code Change Guidelines

- **Minimal changes only.** Make the smallest possible modification that fully addresses the issue. Avoid refactoring unrelated code, renaming unrelated symbols, or restructuring unrelated files.
- **No regressions.** Run the full test suite before and after your changes. Do not remove or modify existing tests unless the test itself is the subject of the issue.
- **Preserve existing patterns.** Follow the conventions already established in the codebase (handler structure, store abstraction, frontend patterns, etc.).
- **Never commit secrets.** The `service-account.json` and any `.env` file must never be committed. Use environment variables for all credentials (see `HOWTO.md`).
- **Backward compatibility.** The JSON store uses a Firestore-compatible schema. If you modify storage keys or shapes, verify that existing stored data will still be read correctly.
- **Responsive UI.** Whenever making changes to views (`src/views/index.html`, `src/views/script.js`, `src/views/styles.css`), always ensure the UI is responsive and works correctly on small screens and mobile devices. Use `@media (max-width: 900px)` blocks to apply mobile-only styles without affecting normal screens.

---

## Deployment

The app is deployed on [Fly.io](https://fly.io). Configuration is in `fly.toml`. Deployment is triggered automatically via the `deploy-production` GitHub Actions workflow on pushes to the main branch. Do not modify deployment configuration unless the issue specifically requires it.

---

## Session Workflow

### 1. Sync with main

```bash
git fetch origin
git pull origin main
```

Start from an up-to-date `main` before branching or making changes.

### 2. Parallel research (Haiku subagents)

Launch two subagents in parallel, both on **Haiku**:

- **Repo explorer** — explores the codebase to find relevant files, existing patterns, and conventions related to the request (see Key source locations above).
- **Best-practices researcher** — searches the internet for current best practices relevant to the request (framework/library conventions, security considerations, etc.).

Both must report back before planning starts.

### 3. Plan (Opus or Fable)

Using the research from step 2, draft an implementation plan with **Opus or Fable**. Use `EnterPlanMode`/`ExitPlanMode` so the plan is presented to the user for approval before any code changes. The plan should break work into a checklist of concrete steps.

**Wait for explicit user approval before proceeding.**

### 4. Implement (Sonnet)

Once approved, implement using **Sonnet**:

- Follow the approved plan as a checklist; check off each item as completed.
- Follow the Code Change Guidelines above (minimal diffs, preserve conventions, no regressions, no secrets).
- Take UI screenshots per the section above when frontend files change.

### 5. Test locally before opening a PR

```bash
python -m unittest discover -s tests -v
pylint $(git ls-files '*.py')
```

Fix failures before proceeding. Do not open a PR with failing tests or lint errors.

### 6. Open the Pull Request

- Push the branch and open a PR via `gh pr create`.
- Include a clear summary, test plan, and UI screenshots (if applicable) in the PR description.

### 7. Watch CI and review comments

- Monitor the PR's GitHub Actions checks until they pass. If CI fails, diagnose and fix, then push updates.
- Watch for reviewer/CI-bot comments on the PR and address them promptly.

### 8. Done when merged

The task is complete only once the PR is merged into `main`. Do not consider the work finished before that point.

---

## Notes

- Never push directly to `main`; always work on a feature branch and go through a PR.
- Never skip step 5 (local testing) to save time — CI failures caught late are more expensive to fix.
- If the user's request is small/trivial, steps 2–3 (subagent research + formal plan) can be lightweight, but should not be skipped entirely — use judgment, but confirm with the user if downscoping.

---

## Useful References

- [README.md](README.md) — Quick-start guide
- [HOWTO.md](HOWTO.md) — Firebase & Firestore setup guide
