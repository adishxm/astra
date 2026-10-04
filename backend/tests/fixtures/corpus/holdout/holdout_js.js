/** Holdout JS test */
const crypto = require('crypto');

function encryptSecret(key, iv, text) {
    // AES-128 cipher
    const cipher = crypto.createCipheriv('aes-128-cbc', key, iv);
    return cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
}

function hashData(buffer) {
    // SHA-512
    return crypto.createHash('sha512').update(buffer).digest('hex');
}

module.exports = { encryptSecret, hashData };
