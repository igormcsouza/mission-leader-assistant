# Claude Instructions for Mission Leader Assistant

For project overview, build/run, linting, and testing commands, see [Agent.md](Agent.md) — read it first.

This file defines the **session workflow** Claude Code should follow for every task on this repo.

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

- **Repo explorer** — explores the codebase to find relevant files, existing patterns, and conventions related to the request (see `src/app.py`, `src/core/`, `src/handlers/`, `src/views/`, `tests/`).
- **Best-practices researcher** — searches the internet for current best practices relevant to the request (framework/library conventions, security considerations, etc.).

Both must report back before planning starts.

### 3. Plan (Opus or Fable)

Using the research from step 2, draft an implementation plan with **Opus or Fable**. Use `EnterPlanMode`/`ExitPlanMode` so the plan is presented to the user for approval before any code changes. The plan should break work into a checklist of concrete steps.

**Wait for explicit user approval before proceeding.**

### 4. Implement (Sonnet)

Once approved, implement using **Sonnet**:

- Follow the approved plan as a checklist; check off each item as completed.
- Follow the **Code Change Guidelines** in [Agent.md](Agent.md) (minimal diffs, preserve conventions, no regressions, no secrets).
- Take UI screenshots per Agent.md when frontend files change.

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
