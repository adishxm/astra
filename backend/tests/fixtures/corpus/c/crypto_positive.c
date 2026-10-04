#include <stdio.h>

void execute_crypto_routines() {
    // OpenSSL EVP algorithm names
    const char *cipher_name = "AES-256";
    const char *asym_algo = "RSA-2048";
    const char *hash_algo = "SHA-256";
    const char *legacy_hash = "MD5";

    printf("Selected crypto: %s, %s, %s, %s\n",
           cipher_name, asym_algo, hash_algo, legacy_hash);
}
