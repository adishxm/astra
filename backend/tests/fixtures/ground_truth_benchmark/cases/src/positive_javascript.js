const crypto = require('crypto');

function encrypt(text, secretKey) {
    const cipher = crypto.createCipheriv('aes-256-gcm', secretKey, Buffer.alloc(12, 0));
    const hash = crypto.createHash('md5').update(text).digest('hex');
    return hash;
}
