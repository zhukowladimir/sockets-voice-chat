package main

import (
	"bufio"
	"log"
	"net"
)

var PORT = ":3333"

type Test struct {
	Qwe string
}

func main() {
	ln, err := net.Listen("tcp", PORT)
	if err != nil {
		log.Fatalln(err)
		return
	}
	defer ln.Close()

	c, err := ln.Accept()
	if err != nil {
		log.Fatalln(err)
		return
	}

	netData, err := bufio.NewReader(c).ReadString('\n')

	if netData != "" {
		log.Printf("Received:\n%s", string(netData))
		c.Write([]byte("How are you, client?"))
	}
}
