-include appstore/Makefile

VERSION=$(shell grep "VERSION =" setup.py|awk -F '"' '{print $$2}')
MAIN=things3_kanban
APP=things3_app
SERVER=things3_api
SERVER_PORT=15000
CLI=things3_cli
SRC_CORE=things3
SRC_TEST=tests
DEST=kanban-static.html
DEST_SRV=http://localhost:$(SERVER_PORT)/kanban.html
PYTHON=python3
PYDOC=pydoc3
PIP=pip3
PIPENV=pipenv

help:
	@echo "CLI, API and Web Service for Things3."
	@echo ""
	@echo "Configuration:"
	@echo " * Static Kanban : $(DEST)"
	@echo " * Dynamic Kanban: $(DEST_SRV)"
	@echo ""
	@echo "Avaliable environment variables:"
	@echo " * THINGSDB    - Path to database"
	@echo " * TAG_WAITING - Tag for tasks you are waiting for"
	@echo " * TAG_MIT     - Tag for most important tassk"
	@echo ""
	@echo "Available commands:"
	@echo " * run          - Run code in static mode."
	@echo " * open         - Open GUI in static mode."
	@echo " * run-api      - Run code in api mode."	
	@echo " * open-api     - Open GUI in api mode in the browser."
	@echo " * kill-api     - Kill code in api mode."
	@echo " * run-app      - Run code in app mode."
	@echo " * cli          - Run code in cli mode (use 'args' for arguments)."
	@echo " * app          - Create KanbanView App."
	@echo " * install      - Install the library and command line tools."
	@echo " * uninstall    - Remove the library and command line tools."
	@echo " * test         - Run unit tests and test coverage."
	@echo " * doc          - Document code (pydoc)."
	@echo " * clean        - Cleanup (e.g. pyc files)."
	@echo " * auto-style   - Automatially style code (autopep8)."
	@echo " * code-style   - Check code style (pycodestyle)."
	@echo " * code-lint    - Check code lints (mypy, pylint, flake8)."
	@echo " * css-lint     - Check CSS styke lints (csslint)."
	@echo " * js-lint      - Check JS code lints (jslint)."
	@echo " * html-lint    - Check HTML file lints (tidy)."
	@echo " * code-count   - Count code lines (cloc)."
	@echo " * deps-install - Install dependencies (see requirements.txt)."
	@echo " * feedback     - Create a GitHub issue."

run:
	@$(PYTHON) -m $(SRC_CORE).$(MAIN)
	@echo "File created: $(DEST)"

open:
	@open $(DEST)

run-api:
	@$(PYTHON) -m $(SRC_CORE).$(SERVER)

open-api:
	@open $(DEST_SRV)

kill-api:
	@lsof -nti:$(SERVER_PORT) | xargs kill

run-app:
	@$(PYTHON) -m $(SRC_CORE).$(APP)

cli:
	@$(PYTHON) -m $(SRC_CORE).$(CLI) $(args)

install:
	@$(PYTHON) setup.py install
	@echo "You can now use 'things-cli', 'things-api' and 'things-kanban'"

uninstall:
	@$(PIP) uninstall -y things3-api


test:
	@type coverage >/dev/null 2>&1 || (echo "Run '$(PIP) install coverage' first." >&2 ; exit 1)
	@coverage erase
	@coverage run -a -m $(SRC_TEST).test_things3
	@coverage run -a -m $(SRC_TEST).test_things3_api
	@coverage run -a -m $(SRC_TEST).test_things3_cli
	@coverage run -a -m $(SRC_TEST).test_things3_kanban
	@coverage report

.PHONY: app
app: clean
	@$(PYTHON) setup.py py2app
	@hdiutil create dist/tmp.dmg -ov -volname "KanbanView" -fs HFS+ -srcfolder "dist"
	@hdiutil convert dist/tmp.dmg -format UDZO -o dist/KanbanView.dmg
	@rm dist/tmp.dmg
	@open dist

.PHONY: doc
doc:
	@$(PYDOC) $(SRC_CORE).things3

.PHONY: clean
clean:
	@rm -f $(DEST)
	@find . -name \*.pyc -delete
	@find . -name __pycache__ -delete
	@rm -rf **/.mypy_cache
	@rm -rf htmlcov
	@rm -rf build dist *.egg-info
	@rm -rf .mypy_cache/
	@rm -f .coverage
	@rm -rf .eggs

auto-style:
	@type black >/dev/null 2>&1 || (echo "Run '$(PIP) install black' first." >&2 ; exit 1)
	@black $(SRC_CORE) $(SRC_TEST) setup.py
	@type standard >/dev/null 2>&1 || (echo "Run 'npm install -g standard' first." >&2 ; exit 1)
	@standard --fix resources/*.js

lint: code-style code-lint js-lint css-lint

code-style:
	@type pycodestyle >/dev/null 2>&1 || (echo "Run '$(PIP) install pycodestyle' first." >&2 ; exit 1)
	@pycodestyle --exclude=*appstore* $(SRC_CORE) $(SRC_TEST)

code-lint:
	@type pylint >/dev/null 2>&1 || (echo "Run '$(PIP) install pylint' first." >&2 ; exit 1)
	@type flake8 >/dev/null 2>&1 || (echo "Run '$(PIP) install flake8' first." >&2 ; exit 1)
	@type mypy >/dev/null 2>&1 || (echo "Run '$(PIP) install mypy' first." >&2 ; exit 1)
	@type vulture >/dev/null 2>&1 || (echo "Run '$(PIP) install vulture' first." >&2 ; exit 1)
	@pip3 show pydiatra >/dev/null 2>&1 || (echo "Run '$(PIP) install pydiatra' first." >&2 ; exit 1)
	@echo "Flake8:" ; $(PYTHON) -m flake8 --max-complexity 10 --exclude=*appstore* $(SRC_CORE) $(SRC_TEST) setup.py
	@echo "Vulture:" ; $(PYTHON) -m vulture $(SRC_CORE) setup.py .vulture-whitelist
	@echo "Pydiatra:" ; $(PYTHON) -m pydiatra $(SRC_CORE)/*.py $(SRC_TEST)/*.py  setup.py
	@echo "Mypy:" ; $(PYTHON) -m mypy --ignore-missing-imports $(SRC_CORE) $(SRC_TEST) setup.py
	@echo "PyLint:" ; $(PYTHON) -m pylint --ignore-patterns=".*appstore.*" $(SRC_CORE)/*.py $(SRC_TEST)/*.py  setup.py

css-lint:
	@type csslint >/dev/null 2>&1 || (echo "Run 'npm install -g csslint' first." >&2 ; exit 1)
	@csslint --format=compact resources/kanban.css

js-lint:
	@type standard >/dev/null 2>&1 || (echo "Run 'npm install -g standard' first." >&2 ; exit 1)
	@standard resources/*.js

html-lint:
	@type tidy >/dev/null 2>&1 || (echo "Run 'brew install tidy' first." >&2 ; exit 1)
	@tidy -qe --mute --mute MISSING_ENDTAG_BEFORE,DISCARDING_UNEXPECTED,TRIM_EMPTY_ELEMENT resources/*.html

code-count:
	@type cloc >/dev/null 2>&1 || (echo "Run 'brew install cloc' first." >&2 ; exit 1)
	@cloc $(SRC_CORE)

deps-install:
	@#type $(PIPENV) >/dev/null 2>&1 || (echo "Run 'brew install pipenv' first." >&2 ; exit 1)
	@$(PIP) install -r requirements.txt
	@#$(PIPENV) install

.PHONY: deps-upgrade
deps-upgrade: ## Upgrade the dependencies
	@if type pip-upgrade >/dev/null 2>&1 ; then pip-upgrade --skip-virtualenv-check requirements.txt ; \
	 else echo "SKIPPED. Run '$(PIP) install pip-upgrade' first." >&2 ; fi

feedback:
	@open https://github.com/AlexanderWillner/KanbanView/issues

pre-commit:
	@rm ~/.kanbanviewrc
	@make clean kill-api
	@make auto-style lint
	@make deps-install install 
	@THINGSDB=resources/demo.sqlite3 things-cli inbox
	@THINGSDB=resources/demo.sqlite3 make run-api &
	@make uninstall clean test jpg
	@THINGSDB=resources/demo.sqlite3 make open-api run open args="today" cli
	@sleep 2
	@make kill-api app
	@THINGSDB=resources/demo.sqlite3 make run-app &
	@open dist/KanbanView.app
	@git status

png:
	@type optipng >/dev/null 2>&1 || (echo "Run 'brew install optipng' first." >&2 ; exit 1)
	@echo "Optimizing PNG..."
	@find . -iname "*.png" -exec optipng -silent {} \;

jpg:
	@type jpegoptim >/dev/null 2>&1 || (echo "Run 'brew install jpegoptim' first." >&2 ; exit 1)
	@echo "Optimizing JPG..."
	@find . -iname "*.jpg" -exec jpegoptim -q {} \;

upload: clean
	@python3 setup.py sdist bdist_wheel
	@python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/things3*

db-to-things:
	@cp resources/demo.sqlite3 ~/Library/Group\ Containers/JLMPQHK86H.com.culturedcode.ThingsMac/ThingsData-*/Things\ Database.thingsdatabase/main.sqlite

db-from-things:
	@cp ~/Library/Group\ Containers/JLMPQHK86H.com.culturedcode.ThingsMac/ThingsData-*/Things\ Database.thingsdatabase/main.sqlite resources/demo.sqlite3
