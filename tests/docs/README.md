# Test Suite Documentation

This folder contains the automated test suite for the **Custom Keyboard Collective** project.

The goal of this test suite is to demonstrate a complete QA strategy for a Django application. It includes tests for business logic, application workflows, REST APIs, browser automation, and performance.

---

# Test Types

The project includes several types of automated tests.

| Folder               | Purpose                                                                                                        |
| -------------------- | -------------------------------------------------------------------------------------------------------------- |
| `tests/unit/`        | Tests for models, forms, helper functions, and business logic.                                                 |
| `tests/integration/` | Tests that verify multiple parts of the application work together, including shopping cart and checkout flows. |
| `tests/api/`         | Tests for REST API endpoints, authentication, request validation, and responses.                               |
| `tests/e2e/`         | End-to-end browser tests using Playwright and the Page Object Model (POM).                                     |
| `tests/smoke/`       | Fast browser tests that confirm the main pages load correctly.                                                 |
| `tests/performance/` | Load testing with Locust to measure application performance under traffic.                                     |

---

# Tools Used

* pytest
* Playwright
* Requests
* Locust
* Coverage.py
* Ruff
* GitHub Actions
* Lefthook

---

# Getting Started

## Requirements

* Python
* Astral uv

Install the project dependencies:

```bash
uv sync
```

Install the Playwright browsers:

```bash
uv run playwright install --with-deps chromium
```

---
# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Run the tests with a coverage summary in the terminal:

```bash
uv run task coverage
```

Generate an HTML coverage report:

```bash
uv run task coverage-report
```

Run only the unit tests:

```bash
uv run pytest tests/unit/
```

Run only the API tests:

```bash
uv run pytest tests/api/
```

Run only the end-to-end tests:

```bash
uv run pytest tests/e2e/
```

Run only the smoke tests:

```bash
uv run pytest tests/smoke/
```

---

# Test Coverage

The latest coverage report shows **99% overall test coverage**.

| Module    | Coverage |
| --------- | -------- |
| account   | 100%     |
| cart      | 96%      |
| inventory | 100%     |
| review    | 100%     |
| shop*     | 100%     |

*Application entry points (`asgi.py` and `wsgi.py`) are not executed during normal test runs, so they are excluded from practical application coverage.

**Overall Coverage: 99%**

---

# Performance Testing

Performance testing is done with **Locust** to simulate users browsing products, logging in, adding items to the cart, and completing checkout.

Start the interactive Locust dashboard:

```bash
uv run task perf
```

Run the headless performance test:

```bash
uv run task perf-report
```

Latest benchmark results:

| Metric                | Result     |
| --------------------- | ---------- |
| Total requests        | **25**     |
| Failure rate          | **0.00%**  |
| Average response time | **41 ms**  |
| Median response time  | **14 ms**  |
| Maximum response time | **191 ms** |

These results show that the application remained stable during the included load test.

---

# Code Quality

The project uses **Lefthook** to automatically run quality checks before code is committed.

The pre-commit workflow includes:

* Ruff formatting
* Ruff linting
* Automated pytest execution

Run the checks manually:

```bash
lefthook run pre-commit --all-files
```
