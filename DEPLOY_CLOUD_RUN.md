# Google Cloud Run Deployment Guide for NIFTY Agents API

## Prerequisites
1. Google Cloud account (free tier: $300 credit for new users)
2. Google Cloud CLI installed: https://cloud.google.com/sdk/docs/install
3. Docker Desktop (optional, for local testing)

## Quick Deploy (5 minutes)

### Step 1: Initialize Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create nifty-agents-api --name="NIFTY Agents API"

# Set the project
gcloud config set project nifty-agents-api

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Store Secrets
```bash
# Store your API keys securely
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo -n "YOUR_SUPABASE_URL" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "YOUR_SUPABASE_KEY" | gcloud secrets create SUPABASE_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
    --member="serviceAccount:$(gcloud iam service-accounts list --filter="displayName:Compute Engine default" --format="value(email)")" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 3: Deploy to Cloud Run
```bash
# Deploy directly from source (Cloud Build will create container)
gcloud run deploy nifty-agents-api \
    --source . \
    --region asia-south1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --timeout 300 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest" \
    --set-env-vars="GEMINI_MODEL=gemini-2.0-flash-exp"
```

### Step 4: Get Your API URL
After deployment, you'll see:
```
Service URL: https://nifty-agents-api-xxxxxxxxxx-el.a.run.app
```

Use this URL in your Next.js dashboard!

## Cloud Run Free Tier Limits
- 2 million requests/month
- 180,000 vCPU-seconds/month  
- 360,000 GB-seconds memory/month
- Generous enough for personal use!

## Cost Estimation
| Usage | Cost |
|-------|------|
| 100 analyses/month | FREE |
| 500 analyses/month | ~$0.50 |
| 1000 analyses/month | ~$1.50 |

## Updating the Deployment
```bash
# After making changes, redeploy:
gcloud run deploy nifty-agents-api --source .
```

## Monitoring
```bash
# View logs
gcloud run logs tail nifty-agents-api

# View in console
# https://console.cloud.google.com/run
```

## Alternative: Firebase Hosting + Cloud Run

If you want to use Firebase for the dashboard:
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Configure firebase.json to proxy API calls to Cloud Run
```

Example `firebase.json`:
```json
{
  "hosting": {
    "public": "dashboard/out",
    "rewrites": [
      {
        "source": "/api/agent/**",
        "run": {
          "serviceId": "nifty-agents-api",
          "region": "asia-south1"
        }
      }
    ]
  }
}
```

## Troubleshooting

### Cold Start Latency
Cloud Run may have 2-5s cold start. To minimize:
```bash
gcloud run services update nifty-agents-api --min-instances=1
```
Note: This will incur costs (~$0.05/hour)

### Memory Issues
If analysis fails with OOM:
```bash
gcloud run services update nifty-agents-api --memory=2Gi
```

### Timeout Issues
Analysis taking too long:
```bash
gcloud run services update nifty-agents-api --timeout=600
```
