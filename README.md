# Missionary Leader Assistant

[![Pylint](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/pylint.yml/badge.svg)](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/pylint.yml)
[![Tests](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/tests.yml/badge.svg)](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/tests.yml)
[![CodeQL](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/igormcsouza/missionary-lunch-calendar/actions/workflows/github-code-scanning/codeql)

Being a mission leader is a great oportunity to serve, even better when we have an application design to help the leader in various aspects of the mission work. This project aims to help those leaders to manage the lunch calendar, visits calendar, baptism plan and much more! Stay tunned for the new features comming up and be free of to focus on the investigators and members of the Church of Jesus Christ of Latter-Days Saints

## Next steps...

I'm happy to keep updating this project and adding more features, if anyone is interested in giving advice just open the issue and I'm going to analyse and implement if it is necessary!

## How to start the development server

In order to be able to run it locally for development one needs to first install [nodemon](https://www.npmjs.com/package/nodemon) to enable `hot reload` and then run the following command in your terminal on the root of the repositoy...

```bash
nodemon --ext py --exec "python3 app.py --dev --host localhost"
```

Make sure to use `--dev` to let the application know that no firestore connection is necessary... And add `--host` to allow firebase to authenticate correctly.

The application will start and restart every time there is a change to the `.py` file. If there are changes to the `.html` file it the UI will catch it.

There is also a Dockerfile and a `docker-compose.yml` for a one-command local startup:

```bash
docker compose up --build
```

The app will be available at `http://localhost:8080` in dev mode (no Google Services should be required).

## Getting Started with Firebase & Firestore

For a step-by-step guide on setting up Firebase Authentication and Firestore (including service accounts, environment variables, Docker, and Fly.io deployment), see [HOWTO.md](HOWTO.md).
