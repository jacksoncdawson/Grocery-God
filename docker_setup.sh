#!/usr/bin/env bash
set -euo pipefail

export REGION=us-west-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export REPO_NAME=grocery-god/scrapers
export ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"

echo "ECR: $ECR_URI"

# Login to ECR
aws ecr get-login-password --region "$REGION" \
| docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Ensure builder exists
docker buildx create --name lambda-builder --use >/dev/null 2>&1 || docker buildx use lambda-builder

# Build amd64 only, and push directly to ECR
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --sbom=false \
  -t "$ECR_URI:latest" \
  --push \
  .

echo "Pushed: $ECR_URI:latest"