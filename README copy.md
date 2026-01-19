# Custom Keyboard Collective — Backend

This repository contains the backend for the **Custom Keyboard Collective** online store.
It's a Django API-first backend and the project is designed to be managed _only_ with **uv** (Astral's `uv` tool) for dependency and environment management.

> This README shows how to develop, run, test and contribute using **uv** exclusively — no `pip`, `virtualenv`, or `python -m venv` commands are required.

---

## Features

- RESTful API for keyboard products, orders, users
- Authentication and authorization
- Input validation and error handling
- Admin dashboard (Django admin) for inventory management

---

## Prerequisites

- A supported OS: macOS, Linux, or Windows
- `uv` installed on your machine (we include install steps below)
- (Optional) Git for cloning and version control

---

## Quick start (step-by-step — using **uv** only)

> All commands below assume you run them from the repository root (the directory created by `git clone`).

1. **Clone the repository**

   ```
   git clone https://github.com/582-41B-VA/custom_keyboard_collective.git
   cd custom_keyboard_collective
   ```

- **Install `uv` if you don't already have it**

  - Homebrew (macOS):

    ```
    brew install uv
    ```

  - Windows (PowerShell):

    ```
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

  After installing, verify with:

  ```
  uv --version
  ```

2. **Running the Project Locally**

   ```
   # create and activate the virtual environment
   uv venv
   ```

   This command creates an isolated virtual environment '.venv' and activates it for the project.

3. **Install/sync dependencies**

   ```
   uv sync
   ```

   This install all required packages as specified in the lock file ('uv.lock'), including Django.

4. **Run the development server**

   ```
   uv run manage.py runserver
   ```

5. **Run tests and linters**

```
uv run manage.py test
uv run ruff check .
```

11. **Common management tasks**

```
# open a Django shell
uv run manage.py shell

# create a migration after model changes
uv run manage.py makemigrations
uv run manage.py migrate

# run custom management scripts
uv run manage.py <command>
```

---

11. **Internationalization**

```
# Each time a new translation is required:
Add the translations inside django.po
uv run django-admin makemessages -l (and the language required, in this is is French) fr
# To compile the translations
uv run django-admin compilemessages
```

---

## Environment variables / secrets

- Store secrets (e.g., `SECRET_KEY`, DB credentials) in environment variables or in a `.env` file that your deployment reads.
- Do **not** commit secrets to source control.

---

## Contributing

- Follow the project's style guidelines.
- Add tests for new features and bug fixes.
- Run `uv run manage.py test` before creating a PR.
- Write clear commit messages and open a PR for review.

---

## Useful `uv` commands reference

- `uv add <package>` — add a dependency and update pyproject / lock
- `uv add --dev <pkg>` — add a dev-only dependency
- `uv sync` — ensure environment matches lockfile
- `uv run <command...>` — run management commands inside the synced environment
- `uvx <tool>` — run a tool temporarily without installing it into the project environment (alias for `uv tool run`)

---

## Troubleshooting

- If `uv run` complains about an out-of-date lockfile, run `uv sync` and re-run the command.
- If ports are already in use, change `--port` or stop the process using that port.

---

## License

This project is for educational purposes only.
