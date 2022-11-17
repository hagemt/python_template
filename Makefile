PACKAGES ?= $(shell find src -name __init__.py -exec dirname {} \;)
PYTHON_3 ?= $(shell command -v python3)
VENV_DIR ?= $(shell pwd)/venv

check: install
	@make format checkstatic test

checkstatic: lint
	@# fails if CVEs or bad types are detected:
	$(VENV_DIR)/bin/bandit -ll -r $(PACKAGES)
	$(VENV_DIR)/bin/mypy $(PACKAGES) tests

clean:
	$(RM) -r '$(VENV_DIR)'
	find . -name '*.pyc' -delete
	@# ^ may reduce noise
	@git clean -dix

dist:
	@git clean -dix
	@make check
	$(VENV_DIR)/bin/python setup.py sdist
	$(VENV_DIR)/bin/python setup.py bdist_wheel
	@# add a `publish: dist` target (to taste)

format: install
	$(VENV_DIR)/bin/isort $(PACKAGES) setup.py tests
	$(VENV_DIR)/bin/black $(PACKAGES) setup.py tests

install:
	@# an ugly but effective way to bootstrap
	@[ -d '$(VENV_DIR)' ] || make venv
	@[ -f '$(VENV_DIR)/ok' ] || make venv.pip
	@touch '$(VENV_DIR)/ok'

lint: install
	$(VENV_DIR)/bin/flake8 $(PACKAGES) tests
	$(VENV_DIR)/bin/pylint $(PACKAGES) tests

test: install
	$(VENV_DIR)/bin/pytest tests --capture=tee-sys --cov
	@#$(VENV_DIR)/bin/coverage report --show-missing
	@# ^ alternative to --cov incl. uncovered lines
.PHONY: check checkstatic clean dist format install lint test

venv:
	[ -x "$(PYTHON_3)" ] && $(PYTHON_3) -m venv '$(VENV_DIR)'
.PHONY: venv

venv.pip:
	source '$(VENV_DIR)/bin/activate' ; \
		pip install -U pip wheel && pip install -e '.[testing]' \
		&& mypy --install-types --non-interactive $(PACKAGES) tests
.PHONY: venv.pip
