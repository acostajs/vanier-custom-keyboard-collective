# Custom Keyboard Collective | Django QA Automation Showcase

A Django e-commerce application built to showcase modern **Software QA and Test Automation** practices. [![codecov](https://codecov.io/gh/acostajs/keyboard-collective-qa-showcase/graph/badge.svg)](https://codecov.io/gh/acostajs/keyboard-collective-qa-showcase)

The project demonstrates how to build and maintain a reliable Python application using automated testing, continuous integration, static analysis, and performance testing. It includes a complete testing strategy covering unit, integration, API, smoke, and end-to-end testing.

The project environment, dependencies, and virtual environments are managed with **Astral uv** for fast and reproducible development.

---

# What This Project Demonstrates

This repository highlights my experience with:

* Building automated test suites with **pytest**
* Writing **unit, integration, API, smoke, and end-to-end tests**
* Creating browser automation with **Playwright** and the **Page Object Model (POM)**
* Running automated tests with **GitHub Actions**
* Supporting multiple Python versions in CI
* Measuring application performance with **Locust**
* Enforcing code quality with **Ruff** and **Git hooks**

For a full overview of the testing strategy, see:

**➡️ [tests/docs/README.md](tests/docs/README.md)**

---

# Tech Stack

### Application

* Django
* Python

### Testing

* pytest
* Playwright
* Requests
* Locust

### Code Quality

* Ruff
* GitHub Actions
* Lefthook

### Development

* Astral uv

---

# Project Structure

```text
tests/
    api/
    docs/
    e2e/
    integration/
    performance/
    smoke/
    unit/

account/
cart/
inventory/
review/
shop/
```

The **tests/** folder contains different types of automated tests:

* **Unit tests** for business logic, models, and helper functions
* **Integration tests** for application workflows
* **API tests** for endpoints, authentication, and request validation
* **End-to-end browser tests** using Playwright
* **Smoke tests** to quickly verify the application starts correctly
* **Performance tests** using Locust

---

# Getting Started

## Requirements

* Python
* Astral uv

Install the project dependencies:

```bash
uv sync
```

Apply the database migrations:

```bash
uv run manage.py migrate
```

Start the development server:

```bash
uv run manage.py runserver
```

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Run the Ruff linter:

```bash
uv run ruff check .
```

Run only a specific test suite:

```bash
uv run pytest tests/unit/
uv run pytest tests/api/
uv run pytest tests/e2e/
uv run pytest tests/smoke/
```

Run the performance tests:

```bash
uv run task perf
```

Generate a performance report:

```bash
uv run task perf-report
```

---

# Continuous Integration

The project includes automated quality checks that run on every commit and pull request.

These checks include:

* Automated test execution
* Static code analysis with Ruff
* Multi-version Python compatibility testing
* Regression testing

---

# License

This project is licensed under the MIT License.
