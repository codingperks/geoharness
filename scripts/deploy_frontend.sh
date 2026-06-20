#!/bin/bash
set -e

BUCKET="ryanperkins-site"
REGION="eu-west-2"
CLOUDFRONT_ID=""  # paste your ryanperkins.dev CloudFront distribution ID here

LATEST_EVAL=$(ls -t eval/solar/results/eval_*.json 2>/dev/null | head -1)
if [ -z "$LATEST_EVAL" ]; then
  echo "No eval results found in eval/solar/results/ — aborting"
  exit 1
fi
echo "Using eval results: $LATEST_EVAL"
cp "$LATEST_EVAL" frontend/data/eval_results.json

echo "Deploying to s3://$BUCKET/geoharness/evaluation/..."
aws s3 sync frontend/ s3://$BUCKET/geoharness/evaluation/ --delete --region $REGION

if [ -n "$CLOUDFRONT_ID" ]; then
  echo "Invalidating CloudFront cache..."
  aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_ID \
    --paths "/geoharness/evaluation/*" > /dev/null
  echo "Done — https://ryanperkins.dev/geoharness/evaluation/"
else
  echo "Done. Set CLOUDFRONT_ID to auto-invalidate on deploy."
fi
