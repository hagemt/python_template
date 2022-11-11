PACKAGES := $(shell find src -name __init__.py -exec dirname {} \;)
PYTHON_3 := $(shell command -v python3)

VENV_DIR := $(shell pwd)/venv

check: install
	@make format checkstatic test
.PHONY: check

checkstatic: lint
	$(VENV_DIR)/bin/bandit -ll -r $(PACKAGES)  # detects CVEs/etc.
	$(VENV_DIR)/bin/mypy --ignore-missing-imports $(PACKAGES) tests

clean:
	$(RM) -r '$(VENV_DIR)'
	find . -name '*.pyc' -delete
	@# ^ reduces noise
	@git clean -dix

dist:
	@git clean -dix
	@make check
	$(VENV_DIR)/bin/python setup.py sdist
	$(VENV_DIR)/bin/python setup.py bdist_wheel

format: install
	$(VENV_DIR)/bin/isort $(PACKAGES) setup.py tests
	$(VENV_DIR)/bin/black $(PACKAGES) setup.py tests

install:
	@# ugly but effective way to bootstrap virtualenv/etc.
	@[ -d '$(VENV_DIR)' ] || $(PYTHON_3) -m venv '$(VENV_DIR)'
	@[ -f '$(VENV_DIR)/ok' ] || make venv.ok
	@touch '$(VENV_DIR)/ok'

lint: install
	$(VENV_DIR)/bin/flake8 $(PACKAGES) tests
	$(VENV_DIR)/bin/pylint $(PACKAGES) tests

test: install
	$(VENV_DIR)/bin/pytest --capture=tee-sys --cov
	@#$(VENV_DIR)/bin/coverage report --show-missing

venv.ok:
	source '$(VENV_DIR)/bin/activate' ; \
		pip install -U pip wheel && pip install -e '.[testing]' \
		&& mypy --install-types --non-interactive $(PACKAGES) tests
.PHONY: check checkstatic clean dist format install lint test venv.ok
