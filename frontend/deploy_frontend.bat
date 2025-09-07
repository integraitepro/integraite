@echo off
REM Integraite Frontend Deployment Script for S3 (Windows)
REM This script builds the React app and deploys it to S3

setlocal enabledelayedexpansion

REM Configuration
set S3_BUCKET=integraite.pro
set DISTRIBUTION_FOLDER=dist

echo 🚀 Starting Integraite Frontend Deployment...

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is not installed. Please install it first.
    echo 📝 Download from: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check AWS credentials
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS credentials not configured or invalid.
    echo 📝 Run: aws configure
    pause
    exit /b 1
)

REM Check if S3 bucket exists
echo 🔍 Checking S3 bucket access...
aws s3 ls s3://%S3_BUCKET% >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot access S3 bucket: %S3_BUCKET%
    echo 📝 Make sure the bucket exists and you have the required permissions.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

REM Build the application
echo 🔨 Building React application...
npm run build

REM Check if build was successful
if not exist "%DISTRIBUTION_FOLDER%" (
    echo ❌ Build failed - %DISTRIBUTION_FOLDER% directory not found.
    pause
    exit /b 1
)

REM Deploy to S3
echo 📤 Uploading files to S3 bucket: %S3_BUCKET%
aws s3 sync %DISTRIBUTION_FOLDER% s3://%S3_BUCKET% --delete

REM Set website configuration
echo 🌐 Configuring S3 website settings...
aws s3 website s3://%S3_BUCKET% --index-document index.html --error-document index.html

echo ""
echo 🎉 Deployment completed successfully!
echo 🌐 Website URL: http://%S3_BUCKET%.s3-website-us-east-1.amazonaws.com
echo ""
pause
