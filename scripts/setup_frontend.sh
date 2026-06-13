#!/bin/bash
set -e

BUCKET="geoharness-frontend"
REGION="eu-west-1"

echo "Creating bucket..."
aws s3 mb s3://$BUCKET --region $REGION

echo "Disabling block public access..."
aws s3api put-public-access-block \
  --bucket $BUCKET \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

echo "Enabling static website hosting..."
aws s3 website s3://$BUCKET \
  --index-document index.html

echo "Setting public read policy..."
aws s3api put-bucket-policy \
  --bucket $BUCKET \
  --policy "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Principal\": \"*\",
      \"Action\": \"s3:GetObject\",
      \"Resource\": \"arn:aws:s3:::$BUCKET/*\"
    }]
  }"

echo "Deploying frontend..."
aws s3 sync frontend/ s3://$BUCKET/ --region $REGION

echo ""
echo "Live at: http://$BUCKET.s3-website-$REGION.amazonaws.com"
