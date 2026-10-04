package main

import (
	"crypto/aes"
	"crypto/md5"
	"crypto/rsa"
	"crypto/sha256"
	"fmt"
)

func RunCryptoRoutines() {
	// AES-256 block cipher initialization
	key := make([]byte, 32)
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	_ = block

	// RSA-2048 key declaration
	rsaKeySize := "RSA-2048"
	fmt.Println(rsaKeySize)

	// SHA-256 and MD5 hashing
	h := sha256.New()
	m := md5.New()
	_ = h
	_ = m
}
