# Makefile
#

PYTHON3=python3

DOCKER_FLAGS?=
DOCKER=docker run $(DOCKER_FLAGS) -ti --rm --network host -v ${PWD}:/app -w /app --name website node:latest

.PHONY: dev
dev:
	@echo === Start dev
	$(DOCKER) /app/start.sh

mm_extract:
	$(PYTHON3) mm/mm_extract.py

#mm_slash:
#	$(PYTHON3) mm/mm_slash.py

mm_publish:
	cd mm && ./mm_publish.sh

mm_clean:
	rm -rf src/_data/facts

