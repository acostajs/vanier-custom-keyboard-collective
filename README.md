# Custom Keyboard Collective — QA & Test Automation Showcase

This repository serves as a professional **QA & Test Automation Showcase**, transforming a Django e-commerce back-end into a resilient, production-grade testing ecosystem. It features an advanced test suite combining isolated unit business logic, multi-version Python compatibility matrices, and automated REST API validation layers.

The entire project lifecycle, dependency locking, and virtual environments are managed exclusively using **`uv`** (Astral’s high-performance Python tooling), ensuring lightning-fast, reproducible test execution.

---

## 🧪 Test Automation Architecture

The core value of this repository lies within its rigorous quality assurance suite. All test executions, fixtures, and execution scripts have been modernized and migrated to a unified architecture.

### [👉 View Full Test Suite Documentation & Execution Guide (tests/docs/README.md)](https://www.google.com/search?q=tests/docs/README.md)

### Test Suite Blueprint

* **Unit Testing (`tests/unit/`):** High-speed, isolated validations targeting product schemas, mechanical keyboard configuration algorithms, and order pricing calculations.
* **Integration Testing (`tests/integration/`):** Verifies database state persistence, Django ORM query optimizations, form submissions, and view layer response integrity.
* **API Testing (`tests/api/`):** Functional endpoint assertions checking REST API payloads, status code behavior (e.g., `200`, `401`, `403`), and token validation.
* **Smoke Testing (`tests/smoke/`):** Fast sanity checks to ensure the application factory initializes and critical core storefront routes boot cleanly.
* **CI/CD & Regression Engine:** Automated workflow pipelines running a multi-Python version compatibility matrix ($3.11 \text{ and } 3.12+$) on every commit and pull request to eliminate regressions.

---

## 🛠️ Quick Start (Local Setup)

All instructions utilize `uv` to ensure instant environment initialization.

### 1. Synchronize Project Environment

Clone the repository and install all project and test-automation dependencies exactly as defined in the lockfile:

```bash
uv sync

```

### 2. Apply Migrations & Seed Database

```bash
uv run manage.py migrate

```

### 3. Execute the Automated Test Suite

Run the test suite headlessly across all modules:

```bash
uv run pytest

```

### 4. Run Static Code Analysis & Linters

Enforce code formatting and quality guardrails across the codebase using Ruff:

```bash
uv run ruff check .

```

### 5. Launch the Application

```bash
uv run manage.py runserver

```

---

## 🚀 Key QA Features for Recruiters

* **No `Any` Type Hinting:** Strict type safety implemented throughout the testing workspace to guarantee contract and payload reliability.
* **DRY Fixture Inheritance:** Centralized setup using a unified global `conftest.py` architecture at the root of the test directory.
* **Modern DevOps Integration:** Pre-configured pre-commit validation engines via `Lefthook` paired with `Ruff` and `Biome` configurations to prevent degraded code from reaching source control.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.