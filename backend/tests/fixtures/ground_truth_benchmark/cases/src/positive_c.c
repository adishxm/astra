#include <stdio.h>
#include <openssl/evp.h>
#include <openssl/sha.h>

void crypto_init() {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, NULL, NULL);
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)"data", 4, hash);
}
