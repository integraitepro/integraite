# Integraite Frontend - S3 Deployment Guide

This guide covers deploying the Integraite frontend React application to AWS S3 with static website hosting.

## Prerequisites

### AWS Requirements
- **AWS Account** with S3 access
- **S3 Bucket**: `integraite.pro` (or your custom domain bucket)
- **IAM Permissions**:
  - `s3:PutObject`
  - `s3:DeleteObject`
  - `s3:GetObject`
  - `s3:ListBucket`
  - `s3:PutBucketWebsite`
  - `s3:PutBucketPolicy`
  - `cloudfront:CreateInvalidation` (if using CloudFront)

### Local Requirements
- **Node.js** 18+ and npm
- **AWS CLI** installed and configured
- **Git** (for cloning)

## Quick Start

### 1. Setup AWS CLI

```bash
# Install AWS CLI (if not already installed)
# Windows: Download from https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: sudo apt install awscli

# Configure AWS credentials
aws configure
```

### 2. Prepare S3 Bucket

```bash
# Create bucket (if it doesn't exist)
aws s3 mb s3://integraite.pro

# Enable static website hosting
aws s3 website s3://integraite.pro --index-document index.html --error-document index.html

# Set public read policy
aws s3api put-bucket-policy --bucket integraite.pro --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::integraite.pro/*"
    }
  ]
}'
```

### 3. Deploy Frontend

```bash
# Navigate to frontend directory
cd frontend

# Create production environment file
cp env.production .env.production
# Edit .env.production with your settings
nano .env.production

# Deploy using the script
chmod +x deploy_frontend.sh
./deploy_frontend.sh
```

## Deployment Methods

### Method 1: Using Deployment Script (Recommended)

**Linux/macOS:**
```bash
./deploy_frontend.sh
```

**Windows:**
```cmd
deploy_frontend.bat
```

The script will:
- ✅ Install dependencies (if needed)
- ✅ Build the React application
- ✅ Upload files to S3 with optimized caching headers
- ✅ Configure S3 website hosting
- ✅ Create backup of previous deployment
- ✅ Invalidate CloudFront cache (if configured)

### Method 2: Manual Deployment

```bash
# Build the application
npm run build

# Sync to S3
aws s3 sync dist/ s3://integraite.pro --delete

# Configure website
aws s3 website s3://integraite.pro --index-document index.html --error-document index.html
```

### Method 3: CI/CD Integration

For GitHub Actions, add this to `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend
on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build application
        run: |
          cd frontend
          npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to S3
        run: |
          cd frontend
          chmod +x deploy_frontend.sh
          ./deploy_frontend.sh
```

## Configuration

### Environment Variables

Create `.env.production` for production builds:

```bash
# API Configuration
VITE_API_BASE_URL=https://api.integraite.pro
VITE_API_VERSION=v1

# Application Settings
VITE_APP_NAME=Integraite
VITE_ENVIRONMENT=production

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false

# External Services
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_MICROSOFT_CLIENT_ID=your-microsoft-client-id
```

### Build Optimization

The deployment script sets optimized caching headers:

- **HTML files**: `no-cache` (always check for updates)
- **CSS/JS files**: `max-age=31536000` (1 year cache)
- **Images**: `max-age=31536000` (1 year cache)
- **Other files**: `max-age=86400` (1 day cache)

### Custom Domain Setup (Optional)

1. **Route 53 Configuration:**
   ```bash
   # Create hosted zone
   aws route53 create-hosted-zone --name integraite.pro --caller-reference $(date +%s)
   
   # Add A record pointing to S3
   # (Use AWS Console for easier setup)
   ```

2. **CloudFront Distribution:**
   ```bash
   # Create distribution pointing to S3 bucket
   # Enable custom SSL certificate
   # Configure caching behaviors
   ```

## Monitoring & Management

### Website Analytics

Access your website at:
- **S3 Website URL**: `http://integraite.pro.s3-website-us-east-1.amazonaws.com`
- **Custom Domain**: `https://integraite.pro` (if configured)

### Cache Management

```bash
# Clear CloudFront cache
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"

# Check invalidation status
aws cloudfront get-invalidation --distribution-id DISTRIBUTION_ID --id INVALIDATION_ID
```

### Backup & Rollback

```bash
# List backups
aws s3 ls s3://integraite.pro/backups/

# Rollback to previous version
aws s3 sync s3://integraite.pro/backups/20240101_120000/ s3://integraite.pro/ --delete
```

## Performance Optimization

### Build Optimization

1. **Bundle Analysis:**
   ```bash
   npm run build -- --analyze
   ```

2. **Code Splitting:**
   - Implemented automatically by Vite
   - Routes are lazy-loaded

3. **Asset Optimization:**
   - Images compressed during build
   - CSS/JS minified and tree-shaken

### CDN Configuration

For optimal performance, consider:

1. **CloudFront Distribution**
2. **Gzip Compression**
3. **HTTP/2 Support**
4. **Edge Locations**

## Troubleshooting

### Common Issues

1. **Build Failures:**
   ```bash
   # Clear cache and rebuild
   rm -rf node_modules dist
   npm install
   npm run build
   ```

2. **AWS Permission Errors:**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Test bucket access
   aws s3 ls s3://integraite.pro
   ```

3. **Website Not Loading:**
   - Check S3 bucket policy
   - Verify website hosting is enabled
   - Check for CORS issues

4. **Stale Content:**
   - Clear browser cache
   - Create CloudFront invalidation
   - Check caching headers

### Performance Issues

1. **Slow Loading:**
   - Enable CloudFront
   - Optimize images
   - Review bundle size

2. **API Connection Issues:**
   - Verify `VITE_API_BASE_URL`
   - Check CORS configuration on backend
   - Test API endpoints directly

## Security Considerations

1. **Environment Variables:**
   - Never commit `.env.production` to version control
   - Use secure secrets management for CI/CD

2. **S3 Bucket Security:**
   - Use least-privilege IAM policies
   - Enable S3 access logging
   - Consider bucket versioning

3. **Content Security:**
   - Implement Content Security Policy (CSP)
   - Use HTTPS for all external resources
   - Validate all user inputs

## Cost Optimization

1. **S3 Storage Classes:**
   - Use Standard for active websites
   - Consider Intelligent Tiering for backups

2. **CloudFront:**
   - Monitor cache hit ratios
   - Configure appropriate TTLs
   - Use price class optimization

3. **Monitoring:**
   - Set up billing alerts
   - Monitor data transfer costs
   - Regular cleanup of old backups

---

For issues or questions, refer to the main project documentation or create an issue in the repository.
