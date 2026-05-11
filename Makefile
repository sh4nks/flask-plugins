.PHONY: clean help sdist release release-test develop test

help:
	@echo "  clean           remove unwanted files"
	@echo "  build           build source + wheel distribution"
	@echo "  release         build and upload to PyPI"
	@echo "  release-test    build and upload to TestPyPI"
	@echo "  docs            build docs"
	@echo "  test            run tests with pytest"

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '.DS_Store' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.coverage' -exec rm -rf {} +

build:
    uv build

release: build
	twine upload --skip-existing dist/{*.tar.gz,*.whl}

release-test: build
	twine upload --repository testpypi --skip-existing dist/{*.tar.gz,*.whl}

docs:
    uv run sphinx-build -E -W -b html docs docs/_build/

test:
	uv run tox
