.PHONY: requirements clean data upgrade

###############
### GLOBALS ###
###############

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PACKAGE_NAME := nflMatchupPredictor

#####################
### MAKE COMMANDS ###
#####################

## Create requirements.txt ##
requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes


## Delete all compiled Python files ##
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

data: requirements
	poetry run python -m $(PACKAGE_NAME)/DataLoaders/CreateDataCli.py DataRepo/Raw DataRepo/Processed

upgrade:
	poetry run python -m pip install -q -U pip