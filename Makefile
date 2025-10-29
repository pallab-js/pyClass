PYTEST=python3 -m pytest

.PHONY: test test-shard1 test-shard2 coverage clean

# Run full test suite without coverage (fast)
test:
	$(PYTEST) -v --tb=short

# Shard 1: models + controllers with coverage but no threshold
test-shard1:
	$(PYTEST) tests/test_models.py tests/test_controllers.py -v --tb=short --cov=. --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=0

# Shard 2: UI + integration with coverage append and enforce threshold
test-shard2:
	$(PYTEST) tests/test_ui_components.py tests/test_integration.py -v --tb=short --cov=. --cov-append --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=html --cov-fail-under=100

coverage: test-shard1 test-shard2

clean:
	rm -rf .pytest_cache htmlcov coverage.xml