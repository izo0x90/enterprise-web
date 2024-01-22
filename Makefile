lint:
	poetry run ruff check .

format:
	poetry run black .

build:
	poetry build

.PHONY: todo
todo:
	@echo "From codebase:\n"
	@grep -r -I --exclude=Makefile --exclude-dir=.ruff_cache 'TODO:' .
	@echo "\n\nFrom todo tracker:\n"
	@cat todo.MD
