package main
import (
    "crypto/sha256"
    "crypto/rsa"
    "crypto/rand"
)

func main() {
    h := sha256.New()
    key, _ := rsa.GenerateKey(rand.Reader, 2048)
    _ = "ML-KEM-768"
}
