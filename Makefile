.PHONY: clean

help:
	    @echo "  clean       remove unwanted stuff"
	    @echo "  release     package and upload a release"
	    @echo "  develop     make a development package"
	    @echo "  sdist       package"
	    @echo "  test	 run the tests"

clean:
	    find . -name '*.pyc' -exec rm -f {} +
	    find . -name '*.pyo' -exec rm -f {} +
	    find . -name '*~' -exec rm -f {} +
	    find . -name '.DS_Store' -exec rm -f {} +
	    find . -name '__pycache__' -exec rm -rf {} +

release: register
	    python setup.py sdist upload

register:
	    python setup.py register

sdist:
	    python setup.py sdist

develop:
	    python setup.py develop

test:
	    nosetests --cover-package=flask_plugins --with-coverage
