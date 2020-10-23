.DEFAULT_GOAL := help
.PHONY: dev test lint start dev_build dev_start dev_test


build:  ## Build all
	docker-compose -f docker-compose-dev.yml build

up:  ## Up All and show logs
	docker-compose -f docker-compose-dev.yml up -d && docker-compose -f docker-compose-dev.yml logs -f --tail=10

stop:  ## Stop all
	docker-compose -f docker-compose-dev.yml stop

down:  ## Down all
	docker-compose -f docker-compose-dev.yml down

test:  ## Run tests
	docker-compose -f docker-compose-dev.yml run --rm bot pytest

lint:  ## Run linters (flake8, mypy)
	flake8 ./bot --count --select=E9,F63,F7,F82 --show-source --statistics --exit-zero --max-complexity=10 --max-line-length=127
	mypy --config-file mypy.ini ./bot

## Help

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done