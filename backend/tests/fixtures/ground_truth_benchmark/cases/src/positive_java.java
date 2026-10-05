// Synthetic positive Java test file
import javax.crypto.Cipher;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;

public class CryptoService {
    public void init() throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(2048);
        MessageDigest md = MessageDigest.getInstance("MD5");
    }
}
