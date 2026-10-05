use ring::aead::{AES_256_GCM, UnboundKey};
use sha2::{Sha256, Digest};

pub fn encrypt_data() {
    let mut hasher = Sha256::new();
    hasher.update(b"payload");
    let result = hasher.finalize();
}
