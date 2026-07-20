# E2E Tests

Python Playwright end-to-end tests for Mission Leader Assistant, driving the real app
in a browser against a live server started with `--dev` (JSON storage, no Google
credentials needed, login is auto-bypassed).

## Install

Uses [`uv`](https://docs.astral.sh/uv/) for package management:

```bash
uv pip install --system -r requirements.txt -r e2e/requirements.txt
playwright install --with-deps chromium
```

Or, for an isolated local virtual environment:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt -r e2e/requirements.txt
playwright install --with-deps chromium
```

## Run

From the repo root:

```bash
pytest e2e/tests -v
```

Run a subset with `-k`:

```bash
pytest e2e/tests -v -k baptismal_plan
```

## Debug

Run headed, with slow-motion, to watch the browser:

```bash
pytest e2e/tests --headed --slowmo 200
```

On failure, screenshots/videos/traces are written to `test-results/` (see
`e2e/pytest.ini`). Open a trace with:

```bash
playwright show-trace test-results/<test-name>/trace.zip
```

## How it works

- `fixtures/server.py` starts `src/app.py --dev` once per test session as a
  subprocess, on a free port, with its working directory set to a throwaway temp
  directory — so the suite never touches your real local `calendar_data.json`.
- `fixtures/data.py` deletes that isolated data file before every test, so each test
  starts from a clean slate without needing to restart the server.
- `pages/` holds Page Object Model wrappers for each view (calendar, settings modal,
  baptismal plan, side drawer).
- Dev mode bypasses Firebase login entirely (hardcoded `X-User-Id: local`), so no
  login flow is needed to reach the app.

## Coverage

See [`COVERAGE.md`](COVERAGE.md) for the feature/bugfix-to-test mapping.
