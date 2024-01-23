# TODO: (Hristo) Clean up setup commands
# API=$(shell docker ps -qf "name=exampleproj-api")
#
# setup-dev-env:
# 	echo "Settign up developement envir."
# 	which brew || echo 'Plese install `brew` package mangager before proceedig!'
# 	which docker || echo 'Plese install `Docker desktop` for MacOs before proceedig!'
# 	which gcloud || echo 'Plese install `Gcloud CLI` tooling before proceedig!'
# 	brew install pyenv
# 	pyenv install 3.11.4
# 	pyenv local 3.11.4
# 	pip install "poetry>=1.7"
# 	poetry self install
# 	poetry install --with dev
# 	echo 'Dev. env. successfully created. `poetry run start` to run the dev. server.'
#
# run:
# 	poetry run start
#
# docker-build:
# 	docker build . -t exampleproj
#
# docker-run:
# 	docker run -p8086:8080 --name exampleproj-api -it --env-file ./docker.env exampleproj  
#
# gcp-setup-project-config:
# 	gcloud config configurations create ec-ai
# 	gcloud auth login --cred-file=../keys/examplecompany-ai-exampleproj-ops.json || echo "Service account key needs to be in ..\keys"
# 	gcloud config set project examplecompany-ai
#
# gcp-activate-project-config:
# 	gcloud config configurations activate ec-ai
#
# gcp-deploy: gcp-activate-project-config
# 	gcloud app deploy
#
# gcp-deploy-logs:
# 	gcloud app logs tail -s exampleproj-api
#
lint:
	poetry run ruff check .

format:
	poetry run black .

start:
	poetry run start

# TODO: (Hristo) Update to use correct build version
rebuild:
	cd .. && poetry build
	poetry remove enterprise-web
	poetry add ../dist/enterprise_web-0.0.0.tar.gz

rebuild-start: rebuild start

.PHONY: todo
todo:
	@grep -r -I --exclude=Makefile --exclude-dir=.ruff_cache 'TODO:' .
