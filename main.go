package main

import (
	"bufio"
	"fmt"
	"github.com/amoghe/distillog"
	"io"
	"math/rand"
	"net"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

const (
	Port     = "SEPPUKU_PORT"
	Listen   = "SEPPUKU_LISTEN"
	Password = "SEPPUKU_PASSWORD"
)

var defaults = map[string]string{
	Listen:   "0.0.0.0",
	Port:     "55192",
	Password: "",
}

// randomPassword generates a random password
func randomPassword(length int) string {
	const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	var sb strings.Builder

	for i := 0; i <= length; i++ {
		sb.WriteByte(
			chars[rand.Intn(len(chars))],
		)
	}
	return sb.String()
}

//goland:noinspection GoUnhandledErrorResult
func handleConnection(conn net.Conn, password string) {
	defer conn.Close()

	reader := bufio.NewReader(conn)

	message, err := reader.ReadString('\n')

	if err != nil {
		if err != io.EOF {
			distillog.Errorf("Error reading from client: %v", err)
		}
		return
	}

	message = message[:len(message)-1] // remove newline character

	distillog.Infof(
		"Received message from %s: %s",
		conn.RemoteAddr().String(),
		message,
	)

	switch message {
	case "ping":
		fmt.Fprintln(conn, "pong")

	case fmt.Sprintf("reboot:%s", password):
		sysrq, err := os.OpenFile(
			"/proc/sys/kernel/sysrq",
			os.O_WRONLY,
			os.ModeAppend,
		)
		defer sysrq.Close()

		if err != nil {
			distillog.Errorf("error %v", err)
			fmt.Fprintln(conn, "error!")
			return
		}
		fmt.Fprintln(sysrq, "1")

		systrigg, err := os.OpenFile(
			"/proc/sysrq-trigger",
			os.O_WRONLY,
			os.ModeAppend,
		)
		defer systrigg.Close()

		if err != nil {
			distillog.Errorf("error %v", err)
			fmt.Fprintln(conn, "error!")
			return
		}
		fmt.Fprintln(systrigg, "b")

	case fmt.Sprintf("nicereboot:%s", password):
		reboot := exec.Command("reboot")
		err := reboot.Run()

		if err != nil {
			distillog.Errorf("Error during reboot %v", err)
			fmt.Fprintln(conn, "error!")
			return
		}
		fmt.Fprintln(conn, "nice reboot")

	default:
		fmt.Fprintln(conn, "???")
	}
}

//goland:noinspection GoUnhandledErrorResult
func run() int {
	listenAddr := os.Getenv(Listen)
	if listenAddr == "" {
		listenAddr = defaults[Listen]
	}

	port := os.Getenv(Port)

	if port == "" {
		port = defaults[Port]
	}

	password := os.Getenv(Password)

	if password == "" {
		password = randomPassword(24)
		distillog.Infof("Random password generated: %s", password)
	}

	listener, err := net.Listen(
		"tcp",
		fmt.Sprintf("%s:%s", listenAddr, port),
	)

	if err != nil {
		distillog.Errorf("Error starting server: %v", err)
		return 1
	}
	defer listener.Close()

	distillog.Infof(
		"Listening on %s",
		listener.Addr().String(),
	)

	for {
		conn, err := listener.Accept()
		if err != nil {
			distillog.Errorf("Error accepting connection: %v", err)
			continue
		}
		go handleConnection(conn, password)
	}
}

func genconfig() int {
	for key, value := range defaults {
		if key != Password {
			fmt.Printf("%s=\"%s\"", key, value)
		} else {
			fmt.Printf("%s=\"%s\"", key, randomPassword(24))
		}

		fmt.Println()
	}
	return 0
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

func main() {
	if runtime.GOOS != "linux" {
		distillog.Errorf("%s is only supported on Linux", os.Args[0])
		os.Exit(2)
		return
	}

	command := "run"

	if len(os.Args) > 1 {
		command = os.Args[1]
	}

	switch command {
	case "run":
		os.Exit(run())
		return

	case "genconfig":
		os.Exit(genconfig())
		return

	case "--help", "-h":
		fmt.Printf("%s [--help|--version|run|genconfig]", os.Args[0])
		fmt.Println()
		fmt.Printf("Version %s [%s]", Version, Commit)
		fmt.Println()
		os.Exit(0)
		return
	}

	os.Exit(1)
}
