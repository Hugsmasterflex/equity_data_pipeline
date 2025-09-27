provider "aws" {
  access_key                  = "minioadmin"
  secret_key                  = "minioadmin"
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_force_path_style         = true
  endpoints {
    s3 = "http://localhost:9000"
  }
}

resource "aws_s3_bucket" "bronze" {
  bucket = "bronze-layer"
}

resource "aws_s3_bucket" "silver" {
  bucket = "silver-layer"
}

resource "aws_s3_bucket" "gold" {
  bucket = "gold-layer"
}
