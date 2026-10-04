resource "aws_kms_key" "data_key" {
  description              = "Customer data key"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
}

resource "aws_kms_key" "rsa_key" {
  description              = "Token signing"
  key_usage                = "SIGN_VERIFY"
  customer_master_key_spec = "RSA_2048"
}

resource "azurerm_key_vault_key" "vault_key" {
  name         = "app-hsm-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 4096
}

resource "azurerm_key_vault_key" "vault_ec" {
  name         = "app-ec-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "EC"
  curve        = "P-256"
}
