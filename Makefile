BIN = $(CURDIR)/bin
CROSS_ARCHS = arm64 arm amd64

generate:
	go generate

build-cross: build
	$(foreach ARCH, $(CROSS_ARCHS), $(shell export GOOS=linux; export GOARCH=$(ARCH); go build -v -o bin/seppuku-$(ARCH)))

build: clean generate
	go build -o $(BIN)/seppuku

clean:
	go clean
	test -f "$(CURDIR)/.commit.txt" && rm "$(CURDIR)/.commit.txt" ; true
	test -d "$(BIN)" && rm -rf "$(BIN)" ; true

run:
	go run main.go

.PHONY: clean build
