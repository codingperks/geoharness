#!/bin/bash
set -e

BUCKET="geoharness-frontend"
REGION="eu-west-1"
CLOUDFRONT_ID=E3NTH8TNRHOB3

echo "Deploying frontend to s3://$BUCKET..."
aws s3 sync frontend/ s3://$BUCKET/ --delete --region $REGION

if [ -n "$CLOUDFRONT_ID" ]; then
  echo "Invalidating CloudFront cache..."
  aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_ID \
    --paths "/*" > /dev/null
  echo "Done (cache invalidation submitted)"
else
  echo "Done: http://$BUCKET.s3-website-$REGION.amazonaws.com"
  echo "Tip: set CLOUDFRONT_ID in your environment to invalidate cache on deploy"
fi
