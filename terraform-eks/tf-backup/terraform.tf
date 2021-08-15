provider "aws" {
  region     = "ap-south-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "test1234xyz-tf-s3bucket"
  # Uncomment this to destroy on resource deletion even s3 contains any file
  #force_destroy = true
  # Enable versioning so we can see the history of files
  versioning {
    enabled = true
  }
  # Comment this lifecycle rule to destroy this resource
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "My bucket"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-dynamodb-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.terraform_state.arn
  description = "The ARN of the S3 bucket"
}
output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "The name of the DynamoDB table"
}