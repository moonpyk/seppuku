BIN = $(CURDIR)/bin
CROSS_ARCHS = arm64 arm amd64

build-cross:
	$(foreach ARCH, $(CROSS_ARCHS), $(shell export GOOS=linux; export GOARCH=$(ARCH); go build -v -o bin/seppuku-$(ARCH)))

build:
	go build -o $(BIN)/seppuku

clean:
	go clean
	rm -rf $(BIN)

run:
	go run main.go

.PHONY: clean build
