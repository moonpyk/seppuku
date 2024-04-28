package main

import _ "embed"

var Version = "0.1"

//go:generate sh -c "printf %s $(git rev-parse HEAD) > .commit.txt"
//go:embed .commit.txt
var Commit string
