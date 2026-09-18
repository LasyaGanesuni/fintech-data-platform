## GitHub Actions / CI/CD — Interview Preparation

We'll start from the mental model, then go into the technical pieces.

### 1. What is CI/CD?

**CI = Continuous Integration**

Whenever developers make changes and push code, automated checks run to make sure the change doesn't break the existing codebase.

Typical flow:

```text
Developer changes code
        ↓
      Git
        ↓
     GitHub
        ↓
 Pull Request / Push
        ↓
 Automated tests
        ↓
      PASS ✓
```

**CD = Continuous Delivery / Deployment**

After the code passes validation, it can be deployed to the target environment.

```text
GitHub
   ↓
CI checks
   ↓
Tests pass
   ↓
Deploy
   ↓
Dev / Test / Prod
```

---

# 2. Why CI/CD for Data Engineering?

Imagine your Databricks project has:

```text
notebooks/
src/
tests/
configs/
```

You change:

```text
src/transformations/deduplication.py
```

Without CI/CD:

```text
Change code
   ↓
Manually test
   ↓
Manually deploy
```

This can lead to human errors.

With CI/CD:

```text
Push code
   ↓
GitHub Actions
   ↓
Run Pytest
   ↓
Validate code
   ↓
Deploy
```

This gives you:

* Automated testing
* Consistent deployment
* Reduced manual errors
* Repeatable releases
* Early detection of broken code

---

# 3. What is GitHub Actions?

**GitHub Actions is GitHub's automation/CI-CD platform.**

You define workflows using YAML files inside:

```text
.github/workflows/
```

For example:

```text
.github/
└── workflows/
    └── ci.yml
```

A workflow can say:

> Whenever code is pushed or a PR is created, run tests.

---

# 4. Basic GitHub Actions structure

A workflow conceptually contains:

```text
Workflow
   ↓
Trigger
   ↓
Jobs
   ↓
Steps
```

Example:

```yaml
name: CI

on:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - checkout code
      - setup Python
      - install dependencies
      - run pytest
```

You don't need to memorize every YAML property.

Understand the structure:

```text
on      → WHEN should workflow run?
jobs    → WHAT work should happen?
steps   → HOW should that work be performed?
```

---

# 5. Triggers

A workflow needs a trigger.

Common triggers:

### Push

```yaml
on:
  push:
    branches:
      - main
```

Runs when code is pushed to `main`.

### Pull Request

```yaml
on:
  pull_request:
```

Runs when a PR is created/updated.

### Manual

GitHub Actions also supports manually triggered workflows.

### Scheduled

Workflows can also run on a schedule.

So:

```text
Push
PR
Manual
Schedule
```

are common trigger concepts.

---

# 6. Jobs

A workflow can contain multiple jobs.

Example:

```text
CI Workflow
   │
   ├── Unit Tests
   │
   ├── Lint
   │
   └── Validation
```

Jobs can sometimes run independently or have dependencies.

For example:

```text
Unit Tests
    ↓
Validation
    ↓
Deployment
```

You don't want deployment to happen if tests fail.

---

# 7. Steps

A job contains steps.

For a Data Engineering project:

```text
Job: Test
   ↓
Checkout repository
   ↓
Setup Python
   ↓
Install dependencies
   ↓
Run Pytest
```

Each step performs one part of the job.

---

# 8. CI/CD for your Databricks project

This is the architecture you should understand for interviews:

```text
Developer
    ↓
Git
    ↓
GitHub
    ↓
Pull Request
    ↓
GitHub Actions
    ↓
 ┌───────────────┐
 │ Unit Tests    │
 │ Code checks   │
 │ Validation    │
 └───────────────┘
    ↓
    PASS
    ↓
Deployment
    ↓
Databricks
```

Later we'll add **Databricks Asset Bundles** into this flow.

```text
GitHub
   ↓
GitHub Actions
   ↓
DAB
   ↓
Databricks
```

---

# 9. CI vs CD in your project

### CI

Primarily validates the code.

Examples:

* Pytest
* Code quality checks
* Validation
* Dependency checks

```text
Developer
 ↓
PR
 ↓
Tests
 ↓
PASS / FAIL
```

### CD

Moves validated code/configuration into an environment.

```text
Validated code
      ↓
    Deploy
      ↓
    Dev
      ↓
   Test
      ↓
   Prod
```

---

# 10. Dev → Test → Prod

A production setup commonly separates environments.

```text
Development
     ↓
Testing
     ↓
Production
```

For example:

```text
Dev Databricks workspace
Test Databricks workspace
Prod Databricks workspace
```

You don't want a developer's experimental code automatically going directly into production.

CI/CD helps create controlled promotion.

---

# 11. Secrets

This is an important interview topic.

You should **not hard-code credentials** inside YAML:

```yaml
password: mypassword
```

Instead, use secure secrets/configuration.

Conceptually:

```text
GitHub Secrets
      ↓
GitHub Actions
      ↓
Deployment
```

Examples:

* Databricks authentication credentials
* Tokens
* Cloud credentials

The exact authentication mechanism can vary by organization and current Databricks setup.

---

# 12. Environment variables vs Secrets

**Environment variable**

Used for configuration.

```text
ENVIRONMENT = dev
```

**Secret**

Used for sensitive information.

```text
TOKEN = ********
```

Don't put sensitive credentials directly into source code.

---

# 13. What happens when a test fails?

Suppose:

```text
Developer
   ↓
PR
   ↓
GitHub Actions
   ↓
Pytest
   ↓
FAIL ❌
```

The pipeline should prevent the next deployment step from proceeding.

Conceptually:

```text
Tests PASS
   ↓
Deploy

Tests FAIL
   ↓
STOP
```

This is one of the biggest benefits of CI/CD.

---

# 14. Why GitHub Actions + Pytest?

This connects directly to what we just learned.

You have:

```text
src/
   schema_validator.py
   deduplication.py
   quarantine.py

tests/
   test_schema_validator.py
   test_deduplication.py
   test_quarantine.py
```

GitHub Actions can automatically run:

```text
pytest
```

whenever a PR is submitted.

So:

```text
Code change
    ↓
GitHub PR
    ↓
GitHub Actions
    ↓
Pytest
    ↓
All tests pass?
   ↙       ↘
 YES       NO
 ↓          ↓
Continue   Stop
```

That's a very useful interview story for you because it connects your **reusable PySpark modules + Pytest + GitHub Actions**.

---

# 15. CI/CD vs Git

Another common question:

> **Is GitHub Actions the same as Git?**

No.

**Git**

→ Version control system.

**GitHub**

→ Platform for hosting/managing Git repositories.

**GitHub Actions**

→ Automation/CI/CD platform integrated with GitHub.

Think:

```text
Git
 ↓
Version control

GitHub
 ↓
Repository / collaboration

GitHub Actions
 ↓
Automation / CI/CD
```

---

## 🎯 Interview skim notes

```text
CI
→ Automatically build/test/validate code changes

CD
→ Automatically deliver/deploy validated changes

GitHub Actions
→ GitHub automation + CI/CD

Workflow
→ YAML automation definition

Trigger
→ Determines WHEN workflow runs

Job
→ Unit of work

Step
→ Individual action within a job

Secrets
→ Secure sensitive configuration

CI example
→ PR → Pytest → validation

CD example
→ Validated code → deploy to Databricks

Typical DE flow
→ Git → GitHub → Actions → Tests → DAB → Databricks

Key principle
→ Don't deploy code that hasn't passed required validation
```

### One interview answer to remember

> **“I would use GitHub Actions to automate CI/CD for the Databricks project. On a pull request, the CI workflow can run unit tests and validation checks. Once those checks pass, the CD workflow can deploy the validated Databricks resources to the appropriate environment. This gives us repeatable deployments and prevents broken code from being promoted.”**
