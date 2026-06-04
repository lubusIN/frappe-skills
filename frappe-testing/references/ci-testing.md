```markdown
# CI Testing Reference

## Overview
Configure continuous integration to run Frappe tests automatically on every commit.

## GitHub Actions

### Basic Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mariadb:
        image: mariadb:10.6
        env:
          MYSQL_ROOT_PASSWORD: root
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install Bench
        run: pip install frappe-bench
      
      - name: Init Bench
        run: |
          bench init --skip-assets --skip-redis-config-generation frappe-bench
          cd frappe-bench
          bench get-app ${{ github.workspace }}
      
      - name: Create Test Site
        run: |
          cd frappe-bench
          bench new-site --db-root-password root --admin-password admin test_site
          bench --site test_site install-app my_app
      
      - name: Run Tests
        run: |
          cd frappe-bench
          bench --site test_site run-tests --app my_app --coverage
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frappe-bench/coverage.xml
```

### Matrix Testing (Multiple Versions)
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        frappe-branch: ['version-15', 'develop']
      fail-fast: false
    
    steps:
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Init Bench
        run: |
          bench init --frappe-branch ${{ matrix.frappe-branch }} frappe-bench
```

### Caching Dependencies
```yaml
      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: ${{ runner.os }}-pip-
      
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

## GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.11

services:
  - mariadb:10.6
  - redis:alpine

variables:
  MYSQL_ROOT_PASSWORD: root
  MYSQL_DATABASE: test_frappe

stages:
  - test

test:
  stage: test
  before_script:
    - pip install frappe-bench
    - bench init --skip-assets frappe-bench
    - cd frappe-bench
    - bench get-app $CI_PROJECT_DIR
    - bench new-site --db-root-password root --admin-password admin test_site
    - bench --site test_site install-app my_app
  script:
    - cd frappe-bench
    - bench --site test_site run-tests --app my_app
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.11
      - image: mariadb:10.6
        environment:
          MYSQL_ROOT_PASSWORD: root
      - image: redis:alpine
    
    steps:
      - checkout
      - run:
          name: Wait for MariaDB
          command: dockerize -wait tcp://127.0.0.1:3306 -timeout 60s
      - run:
          name: Install and Test
          command: |
            pip install frappe-bench
            bench init frappe-bench
            cd frappe-bench
            bench get-app ~/project
            bench new-site --db-root-password root test_site
            bench --site test_site install-app my_app
            bench --site test_site run-tests --app my_app

workflows:
  test_workflow:
    jobs:
      - test
```

## Test Configuration

### pytest.ini
```ini
[pytest]
addopts = -v --tb=short
testpaths = my_app
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = my_app
omit = 
    */test_*.py
    */tests/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

## Parallel Testing

```yaml
      - name: Run Tests (parallel)
        run: |
          cd frappe-bench
          # Split tests across matrix jobs
          bench --site test_site run-tests --app my_app --split ${{ strategy.job-index }}/${{ strategy.job-total }}
```

## UI Tests in CI

```yaml
  ui-test:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      # ... setup steps ...
      
      - name: Start Frappe
        run: |
          cd frappe-bench
          bench serve &
          sleep 10
      
      - name: Run UI Tests
        run: |
          cd frappe-bench
          bench --site test_site run-ui-tests my_app --headless
      
      - name: Upload Screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: cypress-screenshots
          path: frappe-bench/apps/my_app/cypress/screenshots
```

## Test Optimization

### Skip Slow Tests
```yaml
      - name: Run Fast Tests
        run: bench --site test_site run-tests --app my_app -m "not slow"
      
      - name: Run Slow Tests  
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: bench --site test_site run-tests --app my_app -m "slow"
```

### Conditional Testing
```yaml
      - name: Get Changed Files
        id: changed
        uses: tj-actions/changed-files@v39
        with:
          files: |
            *.py
            *.js
      
      - name: Run Tests
        if: steps.changed.outputs.any_changed == 'true'
        run: bench --site test_site run-tests --app my_app
```

## Notifications

```yaml
      - name: Notify Slack on Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Tests failed on ${{ github.ref }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "❌ Tests failed in *${{ github.repository }}*"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Best Practices

1. **Run tests on every PR** — Catch issues before merge
2. **Use caching** — Speed up builds with dependency caching
3. **Parallel testing** — Split tests across multiple runners
4. **Test matrix** — Test against multiple Python/Frappe versions
5. **Upload artifacts** — Save logs and screenshots on failure
6. **Set timeouts** — Prevent hung builds from blocking pipeline

Sources: GitHub Actions, Testing, CI/CD (official docs)
```