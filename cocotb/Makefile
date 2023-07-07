#-----------------------------
# Variable Setups
#-----------------------------
SHELL := /bin/bash

#-----------------------------
# Help text
#-----------------------------
define help_guide =

------------------------------
        HELP GUIDANCE!
------------------------------

Use the following options for this Makefile.
E.g.,   make clean-all

help                                Displays this help menu
clean-all                           Cleans simulation builds
run-log-all                         Runs pytest for all tests with verbose log (e.g., -v -o log_cli=True)
run-all                             Runs pytest for all tessts without verbose log
test test_name="test_name.py"       Runs specific test_name.py without verbose logs
test-log test_name="test_name.py"   Runs specific test_name.py with verbose logs

endef

#-----------------------------
# Actual commands
#-----------------------------
help:
	$(info $(help_guide))

clean-all:
	rm -rf sim_build
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf modelsim.ini
	rm -rf transcript
	rm -rf results.xml

run-log-all: clean-all
	pytest -v -o log_cli=True

run-all: clean-all
	pytest

test:
	@echo "Running test $(test_name)"
	pytest $(test_name)

test-log:
	@echo "Running test $(test_name)"
	pytest $(test_name) -v -o log_cli=True