#!/bin/bash
set -e

BUCKET="geoharness-frontend"
REGION="eu-west-1"
ORIGIN="$BUCKET.s3-website-$REGION.amazonaws.com"

echo "Creating CloudFront distribution..."
DISTRIBUTION=$(aws cloudfront create-distribution \
  --distribution-config "{
    \"CallerReference\": \"geoharness-$(date +%s)\",
    \"Comment\": \"GeoHarness frontend\",
    \"DefaultCacheBehavior\": {
      \"TargetOriginId\": \"S3-$BUCKET\",
      \"ViewerProtocolPolicy\": \"redirect-to-https\",
      \"CachePolicyId\": \"658327ea-f89d-4fab-a63d-7e88639e58f6\",
      \"AllowedMethods\": {
        \"Quantity\": 2,
        \"Items\": [\"GET\", \"HEAD\"]
      }
    },
    \"Origins\": {
      \"Quantity\": 1,
      \"Items\": [{
        \"Id\": \"S3-$BUCKET\",
        \"DomainName\": \"$ORIGIN\",
        \"CustomOriginConfig\": {
          \"HTTPPort\": 80,
          \"HTTPSPort\": 443,
          \"OriginProtocolPolicy\": \"http-only\"
        }
      }]
    },
    \"Enabled\": true,
    \"DefaultRootObject\": \"index.html\"
  }")

DOMAIN=$(echo $DISTRIBUTION | python3 -c "import sys,json; print(json.load(sys.stdin)['Distribution']['DomainName'])")
DIST_ID=$(echo $DISTRIBUTION | python3 -c "import sys,json; print(json.load(sys.stdin)['Distribution']['Id'])")

echo ""
echo "Distribution ID: $DIST_ID"
echo "Live at: https://$DOMAIN  (takes ~10 min to deploy)"
echo ""
echo "Add CLOUDFRONT_ID=$DIST_ID to your .env or note it for cache invalidation"
