VERSION = 1.6

PKG = ciscocli

.DEFAULT_GOAL = version
.PHONY: version
version:
	@ echo "Script version:" $(VERSION)


.PHONY: run
run:  
	@ /usr/bin/env python manage.py run


.PHONY: coverage
coverage: ARGS = "-v"
coverage: 
	@ rm -rf tests/htmlcov
	@ py.test tests --cov-config .coveragerc --cov-report html --cov=$(PKG) ${ARGS}


.PHONY: test
test: ARGS = "-vx"
test: 
	@ py.test tests ${ARGS}


.PHONY: clean
clean:  
	@ find . -name "*.pyc" -delete
	@ find . -name "*.orig" -delete


.PHONY: requirements
requirements:
	@ /usr/bin/env pip install -r requirements.txt

.PHONY: requirements-test
requirements-test:
	@ /usr/bin/env pip install pytest pyhamcrest pytest-cov

.PHONY: requirements-dev
requirements-dev:
	@ /usr/bin/env pip install ipython ptvsd


.PHONY: dependencies
dependencies:
	@ /usr/bin/env pip install -U pip


.PHONY: prepare
prepare: dependencies requirements

.PHONY: prepare-test
prepare-test: prepare requirements-test

.PHONY: prepare-dev
prepare-dev: prepare-test requirements-dev


.PHONY: shell
shell:
	@ /bin/sh

.PHONY: python
python: 
	@ /usr/bin/env python


.PHONY: pack
pack: prepare build

.PHONY: build
build: RUN_FILE = manage.py
build: BUILD_FOLDER = ../build
build: NAME = netdev
build: 
	@ rm -rf $(BUILD_FOLDER)/*
	@ pyinstaller -F \
	    --exclude-module PyInstaller \
	    --specpath "$(BUILD_FOLDER)" \
	    --distpath "$(BUILD_FOLDER)/dist" \
	    --workpath "$(BUILD_FOLDER)/build" \
		--name "$(NAME)" \
	    $(RUN_FILE)
	@ $(MAKE) clean
