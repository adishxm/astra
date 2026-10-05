resource "aws_kms_key" "app_key" {
  description             = "KMS key for app encryption"
  deletion_window_in_days = 10
  customer_master_key_spec = "RSA_2048"
}
