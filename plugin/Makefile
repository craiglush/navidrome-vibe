PLUGIN_NAME = vibe-playlists
WASM_FILE = plugin.wasm
NDP_FILE = $(PLUGIN_NAME).ndp

.PHONY: build package docker-build test clean

build:
	@if command -v tinygo > /dev/null 2>&1; then \
		echo "Building with TinyGo..."; \
		tinygo build -opt=2 -scheduler=none -no-debug \
			-o $(WASM_FILE) -target wasip1 -buildmode=c-shared .; \
	else \
		echo "Building with Go..."; \
		GOOS=wasip1 GOARCH=wasm go build -buildmode=c-shared -o $(WASM_FILE) .; \
	fi

package: build
	zip $(NDP_FILE) $(WASM_FILE) manifest.json

docker-build:
	docker run --rm -v "$(CURDIR):/src" -w /src tinygo/tinygo:latest \
		tinygo build -opt=2 -scheduler=none -no-debug \
		-o $(WASM_FILE) -target wasip1 -buildmode=c-shared .
	zip $(NDP_FILE) $(WASM_FILE) manifest.json

test:
	docker run --rm -v "$(CURDIR):/src" -w /src golang:1.25 go test ./...

clean:
	rm -f $(WASM_FILE) $(NDP_FILE)
