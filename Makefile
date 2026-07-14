.PHONY: build clean test termux

build:
	uv run pyinstaller build.spec --clean

clean:
	rm -rf build/ dist/ *.spec.bak

test:
	uv run pytest tests/ -v

termux:
	bash build_termux.sh
