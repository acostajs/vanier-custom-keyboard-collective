# Custom Keyboard Collective — Backend

This repository contains the backend for the **Custom Keyboard Collective** online store.

The project is built with **Django** and follows an API-first approach. Dependency management and environment setup are handled **exclusively with `uv`** (Astral’s Python tooling). No `pip`, `virtualenv`, or `python -m venv` workflows are used.

> This README explains how to set up, run, test, and contribute to the project using **uv only**.

---

## Overview

The backend provides the core services for the store, including product management, user accounts, and order processing. It is designed to be straightforward to run locally and easy for other developers to understand and extend.

---

## Features

* RESTful API for products, orders, and users
* Authentication and authorization
* Input validation and consistent error handling
* Django admin dashboard for inventory and data management

---

## Prerequisites

* macOS, Linux, or Windows
* `uv` installed locally (installation steps below)
* Git (recommended for cloning and version control)

---

## Quick Start (using **uv** only)

All commands below should be run from the repository root.

### 1. Clone the repository

```bash
git clone https://github.com/582-41B-VA/custom_keyboard_collective.git
cd custom_keyboard_collective
```

### 2. Install `uv` (if not already installed)

**macOS (Homebrew):**

```bash
brew install uv
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify the installation:

```bash
uv --version
```

---

### 3. Create the virtual environment

```bash
uv venv
```

This creates and activates a local virtual environment in `.venv`.

---

### 4. Install dependencies

```bash
uv sync
```

This installs all required dependencies exactly as defined in `uv.lock`.

---

### 5. Run the development server

```bash
uv run manage.py runserver
```

The API will now be available locally.

---

## Testing and Linting

Run the test suite:

```bash
uv run manage.py test
```

Run the linter:

```bash
uv run ruff check .
```

---

## Common Django Management Tasks

```bash
# Open a Django shell
uv run manage.py shell

# Create and apply migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Run any custom management command
uv run manage.py <command>
```

---

## Internationalization (i18n)

When adding or updating translations:

```bash
# Generate message files (example: French)
uv run django-admin makemessages -l fr

# Compile translations
uv run django-admin compilemessages
```

Translations should be edited in the generated `django.po` files.

---

## Environment Variables and Secrets

* Store sensitive values (e.g. `SECRET_KEY`, database credentials) in environment variables or a `.env` file used by your deployment setup.
* Never commit secrets to source control.

---

## Contributing

* Follow the existing code style and project structure
* Include tests for new features and bug fixes
* Run tests before opening a pull request
* Write clear, descriptive commit messages

---

## Useful `uv` Commands

* `uv add <package>` — add a runtime dependency
* `uv add --dev <package>` — add a development-only dependency
* `uv sync` — sync the environment with the lockfile
* `uv run <command>` — run a command inside the project environment
* `uvx <tool>` — run a one-off tool without adding it to the project

---

## Troubleshooting

* If `uv run` reports an out-of-date lockfile, run `uv sync` and retry.
* If the development server fails to start due to a port conflict, stop the existing process or run the server on a different port.

---

## License

This project is for educational purposes only.