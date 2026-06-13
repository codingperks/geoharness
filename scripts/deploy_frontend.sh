#!/bin/bash
set -e

BUCKET="geoharness-frontend"
REGION="eu-west-1"

echo "Deploying frontend to s3://$BUCKET..."
aws s3 sync frontend/ s3://$BUCKET/ --delete --region $REGION

echo "Done: http://$BUCKET.s3-website-$REGION.amazonaws.com"
