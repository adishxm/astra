/**
 * Positive cryptographic usage in Node.js / JavaScript.
 */
const crypto = require('crypto');

function createAesCipher(secretKey, iv) {
    // AES-256 encryption
    return crypto.createCipheriv('aes-256-gcm', secretKey, iv);
}

function computeHashes(buffer) {
    // SHA-256 and legacy MD5
    const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');
    const md5 = crypto.createHash('md5').update(buffer).digest('hex');
    return { sha256, md5 };
}

function verifyRsaSignature(publicKey, signature, data) {
    // RSA-2048 signature verification
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(data);
    return verifier.verify(publicKey, signature);
}

module.exports = { createAesCipher, computeHashes, verifyRsaSignature };
