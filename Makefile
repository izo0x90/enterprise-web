lint:
	poetry run ruff check .

format:
	poetry run ruff format .

build:
	poetry build

.PHONY: todo
todo:
	@echo "From codebase:\n"
	@grep -r -I --exclude=Makefile --exclude-dir=.ruff_cache --exclude=todo.MD 'TODO:' .
	@echo "\n\nFrom todo tracker:\n"
	@cat todo.MD
