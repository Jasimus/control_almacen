.PHONY: build clean test

build:
	uv run pyinstaller build.spec --clean

clean:
	rm -rf build/ dist/ *.spec.bak

test:
	uv run pytest tests/ -v
