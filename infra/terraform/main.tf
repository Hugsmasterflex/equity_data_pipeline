terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  access_key                   = "minioadmin"
  secret_key                   = "minioadmin"
  region                       = "us-east-1"

  # MinIO isn’t real AWS, so skip these checks
  skip_credentials_validation  = true
  skip_metadata_api_check      = true
  skip_requesting_account_id   = true
  skip_region_validation       = true

  # 👉 Force path-style addressing (http://localhost:9000/bucket)
  s3_use_path_style            = true

  endpoints {
    s3 = "http://localhost:9000"
  }
}

# Bronze layer (raw data)
resource "aws_s3_bucket" "bronze" {
  bucket = "bronze-layer"
}

# Silver layer (cleaned/normalized data)
resource "aws_s3_bucket" "silver" {
  bucket = "silver-layer"
}

# Gold layer (aggregated/metrics data)
resource "aws_s3_bucket" "gold" {
  bucket = "gold-layer"
}
