# Makefile
#

DOCKER_FLAGS?=
DOCKER=docker run $(DOCKER_FLAGS) -ti --rm --network host -v ${PWD}:/app -w /app --name website node:latest

.PHONY: dev
dev:
	@echo === Start dev
	$(DOCKER) /app/start.sh