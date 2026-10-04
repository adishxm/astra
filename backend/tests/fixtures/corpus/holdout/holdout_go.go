package main

import (
	"crypto/ed25519"
	"crypto/sha512"
)

func RunHoldout() {
	// Ed25519 signing
	pub, priv, _ := ed25519.GenerateKey(nil)
	_ = pub
	_ = priv

	// SHA-512 hashing
	h := sha512.New()
	_ = h
}
