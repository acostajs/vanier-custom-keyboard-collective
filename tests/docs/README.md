# Custom Collective - Testing Suite

Welcome to the test suite documentation for Custom Collective. This project uses `pytest` as its primary test runner and runner environment, integrated with Playwright for E2E/smoke testing and `requests` for API integration testing.

## CI & Coverage Status

[![continuous-integration](https://github.com/acostajs/vanier-custom-keyboard-collective/actions/workflows/ci.yml/badge.svg)](https://github.com/acostajs/vanier-custom-keyboard-collective/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)

---

## Test Architecture & Organization

The tests are organized logically inside the `tests/` directory as follows:

```
tests/
├── api/             # API Integration tests using `requests`
├── docs/            # Testing documentation (this file)
├── e2e/             # End-to-End User Journey tests using Playwright & Page Object Model
├── integration/     # Service/Flow integration tests (e.g. checkout & cart flow)
├── smoke/           # Playwright tests for server & page health checks
├── unit/            # Classless unit tests for models, forms, and business logic
└── conftest.py      # Centralized pytest configuration and global fixtures
```

### 1. Unit Tests (`tests/unit/`)
These verify the lowest levels of code isolation (e.g., model logic, helper functions, utility validations). 
* **Guidelines**: No class structures are allowed. All test suites are structured as standalone classless functions.
* **Key Files**:
  - `test_account.py` (Account and wishlist logic)
  - `test_cart.py` (Order, Cart, and CartItem models)
  - `test_inventory.py` (Category and Product properties)
  - `test_review.py` (Reviews, comments, voting, and flagging constraints)
  - `test_helpers.py` (Price conversion and parsing utilities)

### 2. Integration Tests (`tests/integration/`)
These test flows across multiple database models and services (e.g., checking catalog searching & filtering, adding items, and validating stripe checkout redirect flows).
* **Key Files**:
  - `test_cart_flow.py`

### 3. API Integration Tests (`tests/api/`)
These make standard HTTP loopback requests against a live test server using the `requests` library. They verify request-response cycles, status codes, payload structures, session preservation, and CSRF token handling.
* **Key Files**:
  - `test_catalog_api.py` (Category/Product search and retrieval)
  - `test_cart_api.py` (Cart adding, updates, clearing, and checkout session endpoint)
  - `test_account_review_api.py` (User registration, login, logout, and authenticated reviews)

### 4. End-to-End (E2E) Tests (`tests/e2e/`)
These test real browser scenarios using Playwright, simulating user actions on front-end components. They follow the Page Object Model (POM) pattern.
* **Key Files**:
  - `pages/` (POM declarations)
  - `test_guest_shopping_journey.py` (Full guest flow from catalog to cart)
  - `test_user_auth_journey.py` (Register, login, account dashboard checks, and logout)

### 5. Smoke Tests (`tests/smoke/`)
These utilize Playwright to quickly run page-load health checks against critical system routes, ensuring that pages respond with HTTP 200 and render the required headings.
* **Key Files**:
  - `test_server_health.py` (Homepage, Category, Product, Login, Registration, and Cart views)

---

## Getting Started & Commands

### Prerequisites
Make sure you have `uv` installed, which serves as the package manager and runner:

```bash
# Verify uv is installed
uv --version
```

### Install Dependencies
To install the testing and project dependencies (configured in `pyproject.toml`):

```bash
# Sync and set up virtual environment
uv sync

# Install Playwright browsers (chromium)
uv run playwright install --with-deps chromium
```

### Running Tests

To run the entire test suite:
```bash
uv run pytest
```

To run a specific directory or test suite:
```bash
# Run unit tests only
uv run pytest tests/unit/

# Run API integration tests only
uv run pytest tests/api/

# Run E2E tests only
uv run pytest tests/e2e/

# Run smoke tests only
uv run pytest tests/smoke/
```

### Code Coverage

Code coverage is automatically enabled by `pytest.ini` using the `pytest-cov` plugin:
- Configuration rules: `--cov=. --cov-report=term-missing`
- To run tests without coverage (e.g. for faster debugging):
```bash
uv run pytest --no-cov
```

---

## Pre-commit Hooks

This project uses `lefthook` to format, lint, and run tests before every git commit.

```bash
# Run pre-commit checks on all files manually
lefthook run pre-commit --all-files
```
The pre-commit hook runs:
- `ruff-format` (Code formatting)
- `ruff-check` (Linting)
- `pytest` (Test validation)
