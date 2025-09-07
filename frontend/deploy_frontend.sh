#!/bin/bash

# Simple Frontend Deployment Script for S3
# This script builds the React app and copies files to S3

set -e  # Exit on any error

# Configuration
S3_BUCKET="integraite.pro"
DISTRIBUTION_FOLDER="dist"

echo "🚀 Starting Frontend Deployment..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Build the application
echo "🔨 Building React application..."
npm run build

# Check if build was successful
if [ ! -d "$DISTRIBUTION_FOLDER" ]; then
    echo "❌ Build failed - $DISTRIBUTION_FOLDER directory not found."
    exit 1
fi

# Copy files to S3
echo "📤 Copying files to S3 bucket: $S3_BUCKET"
aws s3 sync $DISTRIBUTION_FOLDER s3://$S3_BUCKET --delete

echo "✅ Deployment completed!"
echo "🌐 Files uploaded to: s3://$S3_BUCKET"
