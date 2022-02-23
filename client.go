package main

import (
	"log"
	"net"
	"strings"
)

var PORT = "3333"
var IP = "127.0.0.1"

func SocketClient() error {
	addr := strings.Join([]string{IP, PORT}, ":")

	conn, err := net.Dial("tcp", addr)
	defer conn.Close()
	if err != nil {
		log.Fatalln(err)
		return err
	}

	helloworld := "Hello, server! I am client!\n"
	conn.Write([]byte(helloworld))
	log.Printf("Send:\n%s\n", helloworld)

	buff := make([]byte, 1024)
	n, err := conn.Read(buff)
	if err != nil {
		log.Fatalln(err)
		return err
	}
	log.Printf("Received:\n%s\n", buff[:n])

	return nil
}

func main() {
	SocketClient()
}
