package com.astra.test;

import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import javax.crypto.Cipher;

public class CryptoPositive {
    public void setupCryptography() throws Exception {
        // RSA-2048 Key Pair Generator
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA-2048");

        // AES-256 Symmetric Encryption
        Cipher cipher = Cipher.getInstance("AES-256");

        // SHA-256 Hash Digest
        MessageDigest sha = MessageDigest.getInstance("SHA-256");

        // Deprecated MD5 Digest
        MessageDigest md5 = MessageDigest.getInstance("MD5");
    }
}
